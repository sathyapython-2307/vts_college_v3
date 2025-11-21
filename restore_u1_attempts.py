#!/usr/bin/env python
import os
import django
import sqlite3
from datetime import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CourseAccess, ExamAttempt, ExamAnswer, ExamViolation, ExamQuestion

BACKUP_DB = os.path.join(os.path.dirname(__file__), 'db_backups', 'db_backup_20251121_133018.sqlite3')
TARGET_USERNAME = 'u1@gmail.com'

if not os.path.exists(BACKUP_DB):
    print('Backup DB not found at', BACKUP_DB)
    exit(1)

# Find user in current DB
current_user = User.objects.filter(username=TARGET_USERNAME).first()
if not current_user:
    print('User not found in current DB:', TARGET_USERNAME)
    exit(1)

print('Current user id:', current_user.id)

conn = sqlite3.connect(BACKUP_DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Find user in backup DB
c.execute("SELECT id, username, email FROM auth_user WHERE username = ?", (TARGET_USERNAME,))
row = c.fetchone()
if not row:
    print('User not found in backup DB:', TARGET_USERNAME)
    conn.close()
    exit(1)

backup_user_id = row['id']
print('Backup user id:', backup_user_id)

# Fetch exam attempts from backup for this user via course_access
c.execute("SELECT ea.* FROM core_examattempt ea JOIN core_courseaccess ca ON ea.course_access_id = ca.id WHERE ca.user_id = ?", (backup_user_id,))
attempts = c.fetchall()
print('Found', len(attempts), 'attempt(s) in backup DB for user')

restored = 0
for a in attempts:
    # Get course_access backup id to find course id
    ca_id = a['course_access_id']
    c.execute('SELECT course_id FROM core_courseaccess WHERE id = ?', (ca_id,))
    ca_row = c.fetchone()
    if not ca_row:
        print('  - course_access', ca_id, 'not found in backup DB, skipping')
        continue
    course_id = ca_row['course_id']
    # Find current CourseAccess for this user and course
    current_ca = CourseAccess.objects.filter(user=current_user, course__id=course_id).first()
    if not current_ca:
        print(f'  - Current CourseAccess for course_id={course_id} not found for user, skipping')
        continue
    # Create new ExamAttempt in current DB
    attempt_kwargs = {
        'course_access': current_ca,
        'attempt_number': a['attempt_number'],
        'started_at': a['started_at'],
        'submitted_at': a['submitted_at'],
        'time_taken_seconds': a['time_taken_seconds'],
        'is_submitted': bool(a['is_submitted']),
        'is_passed': a['is_passed'],
        'score_percentage': a['score_percentage'],
        'correct_answers': a['correct_answers'],
        'total_questions': a['total_questions'],
        'has_violations': bool(a['has_violations']),
        'violation_count': a['violation_count']
    }
    # Parse string timestamps if necessary
    for k in ('started_at','submitted_at'):
        if attempt_kwargs.get(k) is not None and isinstance(attempt_kwargs[k], str):
            try:
                attempt_kwargs[k] = datetime.fromisoformat(attempt_kwargs[k])
            except Exception:
                attempt_kwargs[k] = None

    # Make datetimes timezone-aware if naive
    for dt_field in ('started_at', 'submitted_at'):
        dt = attempt_kwargs.get(dt_field)
        if isinstance(dt, datetime) and timezone.is_naive(dt):
            attempt_kwargs[dt_field] = timezone.make_aware(dt, timezone.get_default_timezone())

    # Create attempt (skip if duplicate attempt_number for this course_access)
    try:
        new_attempt = ExamAttempt.objects.create(**attempt_kwargs)
    except Exception as e:
        print(f"  - Skipping restore for course_id={course_id} attempt_number={attempt_kwargs.get('attempt_number')} due to: {e}")
        continue
    print(f'  - Restored ExamAttempt id={new_attempt.id} for course_id={course_id}, attempt_number={new_attempt.attempt_number}')
    restored += 1

    # Restore answers
    c.execute('SELECT * FROM core_examanswer WHERE attempt_id = ?', (a['id'],))
    answers = c.fetchall()
    for ans in answers:
        # Map question id assuming consistent ids
        try:
            q = ExamQuestion.objects.get(id=ans['question_id'])
        except ExamQuestion.DoesNotExist:
            print('    - Question id', ans['question_id'], 'not found in current DB, skipping answer')
            continue
        ExamAnswer.objects.create(
            attempt=new_attempt,
            question=q,
            selected_answer=ans['selected_answer'],
            is_correct=bool(ans['is_correct'])
        )
    # Restore violations
    c.execute('SELECT * FROM core_examviolation WHERE attempt_id = ?', (a['id'],))
    violations = c.fetchall()
    for v in violations:
        ExamViolation.objects.create(
            attempt=new_attempt,
            violation_type=v['violation_type'],
            violation_count=v['violation_count'],
            description=v['description'] or '',
            auto_submitted=bool(v['auto_submitted'])
        )

conn.close()
print('Restored', restored, 'attempt(s)')
print('Done')
