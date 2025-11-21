#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ExamAttempt, CourseProgress

USERNAME = 'u1@gmail.com'

user = User.objects.filter(username=USERNAME).first()
if not user:
    print('User not found:', USERNAME)
    exit(1)

# Count existing attempts
attempts_qs = ExamAttempt.objects.filter(course_access__user=user)
count_before = attempts_qs.count()
print('Found', count_before, 'ExamAttempt row(s) for', USERNAME)

# Delete attempts (will cascade delete answers/violations)
deleted_info = attempts_qs.delete()
# deleted_info is a tuple (n_deleted, { 'app.Model': n, ... })
print('Deletion result:', deleted_info)

# Clear ready_for_exam flags on CourseProgress for this user
cp_qs = CourseProgress.objects.filter(course_access__user=user, ready_for_exam=True)
cp_count = cp_qs.count()
if cp_count:
    cp_qs.update(ready_for_exam=False, ready_for_exam_date=None)
    print('Cleared ready_for_exam on', cp_count, 'CourseProgress record(s)')
else:
    print('No CourseProgress records with ready_for_exam=True found for user')

# Final counts
final_count = ExamAttempt.objects.filter(course_access__user=user).count()
print('Remaining ExamAttempt rows for user:', final_count)
print('Done')
