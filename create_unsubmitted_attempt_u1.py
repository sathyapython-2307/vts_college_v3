#!/usr/bin/env python
import os
import django
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CourseAccess, ExamAttempt, CourseExam

USERNAME = 'u1@gmail.com'
COURSE_ID = 3  # course where attempts exist (from listing)

user = User.objects.filter(username=USERNAME).first()
if not user:
    print('User not found:', USERNAME)
    exit(1)

ca = CourseAccess.objects.filter(user=user, course__id=COURSE_ID).first()
if not ca:
    print('CourseAccess for user not found for course id', COURSE_ID)
    exit(1)

# Determine next attempt number
existing = ExamAttempt.objects.filter(course_access=ca)
if existing.exists():
    next_attempt = existing.order_by('-attempt_number').first().attempt_number + 1
else:
    next_attempt = 1

# Determine total questions from CourseExam
total_q = 0
try:
    ce = CourseExam.objects.get(course__id=COURSE_ID)
    total_q = ce.questions.filter(is_active=True).count()
except Exception:
    total_q = 0

attempt = ExamAttempt.objects.create(
    course_access=ca,
    attempt_number=next_attempt,
    started_at=timezone.now(),
    submitted_at=None,
    time_taken_seconds=None,
    is_submitted=False,
    is_passed=None,
    score_percentage=None,
    correct_answers=0,
    total_questions=total_q,
    has_violations=False,
    violation_count=0
)
print('Created unsubmitted ExamAttempt:', attempt.id, 'course_id=', COURSE_ID, 'attempt_number=', attempt.attempt_number)
