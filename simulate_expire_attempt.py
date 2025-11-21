#!/usr/bin/env python
import os
import django
import json
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')

django.setup()

from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import ExamAttempt, Course
from core import exam_views

User = get_user_model()
user = User.objects.filter(username='u2@gmail.com').first()
if not user:
    print('User not found')
    exit(1)

# pick latest attempt or create new via exam_start
attempt = ExamAttempt.objects.filter(course_access__user=user).order_by('-id').first()
if not attempt:
    print('No attempts for user currently. To test, start an exam manually from UI.')
    exit(1)

print('Found attempt', attempt.id, 'submitted?', attempt.is_submitted)

# Force started_at far in past to simulate expiration
attempt.started_at = timezone.now() - timedelta(minutes=200)
attempt.save()

factory = RequestFactory()
request = factory.get(f'/exam/{attempt.id}/time-left/')
request.user = user

resp = exam_views.exam_time_left(request, attempt.id)
print('Time-left view response (auto-submission should trigger if expired):')
print(resp.content.decode('utf-8'))

# reload attempt
attempt.refresh_from_db()
print('Attempt submitted after calling time-left?', attempt.is_submitted)
print('score_percentage:', attempt.score_percentage)
