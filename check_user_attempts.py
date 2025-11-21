#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import ExamAttempt

User = get_user_model()
user = User.objects.filter(username='u2@gmail.com').first()
if not user:
    print('User not found')
    exit(0)

attempts = ExamAttempt.objects.filter(course_access__user=user)
print('User:', user.email)
print('Attempts count:', attempts.count())
for a in attempts:
    print('Attempt ID:', a.id, 'Submitted:', a.is_submitted, 'Started:', a.started_at)
