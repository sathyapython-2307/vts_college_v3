#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ExamAttempt

USERNAME = 'u1@gmail.com'
user = User.objects.filter(username=USERNAME).first()
if not user:
    print('User not found:', USERNAME)
    exit(1)

attempts = ExamAttempt.objects.filter(course_access__user=user, is_submitted=True)
print(f'Found {attempts.count()} submitted attempt(s) for user {USERNAME}:')
for a in attempts:
    print(f'  - id={a.id} course_id={a.course_access.course.id} attempt_number={a.attempt_number} submitted_at={a.submitted_at}')
