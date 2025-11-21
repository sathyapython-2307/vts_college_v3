#!/usr/bin/env python3
"""
Reset development data script
- Backs up the SQLite database (timestamped copy)
- Deletes all non-superuser users and related user-generated records
- Produces a restore PowerShell script to roll back by copying the backup file back

USAGE: run from project root where `manage.py` lives:
    venv\Scripts\Activate
    python scripts\reset_dev_data.py

This script will abort if the Django settings indicate DEBUG=False or
if the default database is not SQLite (to avoid accidental production runs).
"""
import os
import sys
import shutil
import datetime
import csv
from pathlib import Path

# Ensure project root is on sys.path so Django settings import works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Set Django settings module and bootstrap
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
try:
    import django
    django.setup()
except Exception as e:
    print('Error setting up Django environment:', e)
    sys.exit(1)

from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model

# Import models we'll clean
try:
    from core import models as core_models
except Exception as e:
    print('Failed to import core models:', e)
    sys.exit(1)

User = get_user_model()

DB_PATH = Path(settings.DATABASES['default'].get('NAME', ''))
if not DB_PATH.is_absolute():
    DB_PATH = (PROJECT_ROOT / DB_PATH).resolve()

TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
BACKUP_DIR = PROJECT_ROOT / 'db_backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_FILE = BACKUP_DIR / f'db_backup_{TIMESTAMP}.sqlite3'
DELETED_USERS_CSV = BACKUP_DIR / f'deleted_users_{TIMESTAMP}.csv'
SUMMARY_FILE = BACKUP_DIR / f'delete_summary_{TIMESTAMP}.txt'
RESTORE_SCRIPT = BACKUP_DIR / f'restore_db_from_backup_{TIMESTAMP}.ps1'

# Safety checks
if not settings.DEBUG:
    print('Refusing to run: settings.DEBUG is False. This must only run on development database.')
    sys.exit(1)

engine = settings.DATABASES['default'].get('ENGINE', '')
if 'sqlite' not in engine:
    print('Refusing to run: default DB engine is not SQLite. This script only supports SQLite development DB.')
    sys.exit(1)

if not DB_PATH.exists():
    print(f'Database file not found at {DB_PATH}')
    sys.exit(1)

# Backup
print('Creating backup of database...')
try:
    shutil.copy2(str(DB_PATH), str(BACKUP_FILE))
    print('Backup created at:', BACKUP_FILE)
except Exception as e:
    print('Failed to create backup:', e)
    sys.exit(1)

# Safety: confirm action with user
print('\nWARNING: This will permanently delete NON-SUPERUSER accounts and associated user-generated data from the development DB.')
confirm = input('Type YES to proceed: ')
if confirm.strip() != 'YES':
    print('Aborting.')
    sys.exit(0)

# Collect non-superuser users
users_qs = User.objects.filter(is_superuser=False)
user_list = list(users_qs.values('id', 'username', 'email', 'is_staff'))
num_users = len(user_list)
print(f'Found {num_users} non-superuser user accounts to delete.')

# Save user list to CSV for auditing
with open(DELETED_USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'username', 'email', 'is_staff'])
    writer.writeheader()
    for row in user_list:
        writer.writerow(row)

# Function to count and delete queryset safely
def count_and_delete(qs):
    try:
        count = qs.count()
    except Exception:
        # Fallback for querysets without count
        count = len(list(qs))
    qs.delete()
    return count

summary_lines = []
summary_lines.append(f'Delete operation timestamp: {TIMESTAMP}')
summary_lines.append(f'Backup file: {BACKUP_FILE}')
summary_lines.append(f'Users CSV: {DELETED_USERS_CSV}')
summary_lines.append('')

# Begin deletion in transaction
from django.db import connection
with transaction.atomic():
    # Video plays
    try:
        vp_qs = core_models.VideoPlay.objects.filter(user__isnull=False, user__is_superuser=False)
        c = count_and_delete(vp_qs)
        summary_lines.append(f'VideoPlay rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'VideoPlay deletion error: {e}')

    # Exam answers and violations and attempts (cascade via CourseAccess but explicit for clarity)
    try:
        ea_qs = core_models.ExamAnswer.objects.filter(attempt__course_access__user__is_superuser=False)
        c = count_and_delete(ea_qs)
        summary_lines.append(f'ExamAnswer rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'ExamAnswer deletion error: {e}')

    try:
        ev_qs = core_models.ExamViolation.objects.filter(attempt__course_access__user__is_superuser=False)
        c = count_and_delete(ev_qs)
        summary_lines.append(f'ExamViolation rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'ExamViolation deletion error: {e}')

    try:
        ea_qs = core_models.ExamAttempt.objects.filter(course_access__user__is_superuser=False)
        c = count_and_delete(ea_qs)
        summary_lines.append(f'ExamAttempt rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'ExamAttempt deletion error: {e}')

    # Certificates and progress
    try:
        cert_qs = core_models.Certificate.objects.filter(course_progress__course_access__user__is_superuser=False)
        c = count_and_delete(cert_qs)
        summary_lines.append(f'Certificate rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'Certificate deletion error: {e}')

    try:
        cp_qs = core_models.CourseProgress.objects.filter(course_access__user__is_superuser=False)
        c = count_and_delete(cp_qs)
        summary_lines.append(f'CourseProgress rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'CourseProgress deletion error: {e}')

    # CourseAccess and CoursePayment
    try:
        payment_qs = core_models.CoursePayment.objects.filter(user__is_superuser=False)
        c = count_and_delete(payment_qs)
        summary_lines.append(f'CoursePayment rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'CoursePayment deletion error: {e}')

    try:
        access_qs = core_models.CourseAccess.objects.filter(user__is_superuser=False)
        c = count_and_delete(access_qs)
        summary_lines.append(f'CourseAccess rows deleted: {c}')
    except Exception as e:
        summary_lines.append(f'CourseAccess deletion error: {e}')

    # Finally delete the User objects themselves
    try:
        users_count = users_qs.count()
        users_qs.delete()
        summary_lines.append(f'User accounts deleted: {users_count}')
    except Exception as e:
        summary_lines.append(f'User deletion error: {e}')

# Write summary
with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(summary_lines))

print('\nDeletion summary:')
for line in summary_lines:
    print(line)

# Create restore PowerShell script
restore_cmd = f"Copy-Item -Path \"{BACKUP_FILE}\" -Destination \"{DB_PATH}\" -Force\nWrite-Host 'Database restored from {BACKUP_FILE} to {DB_PATH}. Restart your Django server if running.'\n"
with open(RESTORE_SCRIPT, 'w', encoding='utf-8') as f:
    f.write(restore_cmd)

print('\nA restore script was written to:', RESTORE_SCRIPT)
print('To roll back, run this PowerShell script (from project root):')
print(f'  powershell -ExecutionPolicy Bypass -File "{RESTORE_SCRIPT}"')
print('\nOperation complete.')
print(f'Backup file: {BACKUP_FILE}')
print(f'Deleted users CSV: {DELETED_USERS_CSV}')
print(f'Summary file: {SUMMARY_FILE}')
