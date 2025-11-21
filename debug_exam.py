#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from core.models import CourseExam, Course, ExamAttempt, CourseAccess
from django.contrib.auth.models import User

# Check course 3 exam
try:
    course = Course.objects.get(id=3)
    exam = CourseExam.objects.get(course=course)
    print(f'✓ Course: {course.name}')
    print(f'✓ Exam max_attempts: {exam.max_attempts}')
    print(f'✓ Exam is_active: {exam.is_active}')
    print(f'✓ Exam questions: {exam.questions.filter(is_active=True).count()}')
except Exception as e:
    print(f'✗ Error: {e}')

# Check all course accesses for course 3
print(f'\nAll users with access to course 3:')
accesses = CourseAccess.objects.filter(course_id=3)
print(f'Total accesses: {accesses.count()}')
for access in accesses:
    user = access.user
    attempts = ExamAttempt.objects.filter(course_access=access)
    print(f'\n  User: {user.email}')
    print(f'  - Active: {access.is_active}')
    print(f'  - Attempts: {attempts.count()}')
    for attempt in attempts:
        print(f'    · Attempt {attempt.attempt_number}: submitted={attempt.is_submitted}, passed={attempt.is_passed}')
