#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CourseAccess, ExamAttempt, CourseProgress

username = 'u1@gmail.com'
user = User.objects.filter(username=username).first()
if not user:
    print(f"User {username} not found")
    exit(1)

print(f"Found user: {user.email} (id={user.id})")

# Delete ExamAttempt rows for this user
attempts_qs = ExamAttempt.objects.filter(course_access__user=user)
count = attempts_qs.count()
print(f"Found {count} exam attempts for user {username}")
if count > 0:
    attempts_qs.delete()
    print(f"Deleted {count} exam attempts")
else:
    print("No exam attempts to delete")

# Clear CourseProgress.ready_for_exam flags for this user's accesses
progress_qs = CourseProgress.objects.filter(course_access__user=user)
prog_count = progress_qs.count()
print(f"Found {prog_count} CourseProgress records for user {username}")
if prog_count > 0:
    updated = progress_qs.update(ready_for_exam=False, ready_for_exam_date=None)
    print(f"Updated {updated} CourseProgress records: cleared ready_for_exam flag")
else:
    print("No CourseProgress records to update")

# Print remaining attempts (should be zero)
remaining = ExamAttempt.objects.filter(course_access__user=user).count()
print(f"Remaining ExamAttempt rows for user: {remaining}")

print('Done.')
