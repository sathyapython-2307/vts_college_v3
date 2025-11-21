#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from core.models import Course, CourseExam, ExamQuestion

# Get all active courses
courses = Course.objects.filter(is_active=True)
print(f"Found {courses.count()} active courses:\n")

for course in courses:
    exam = CourseExam.objects.filter(course=course, is_active=True).first()
    if exam:
        q_count = exam.questions.filter(is_active=True).count()
        print(f"  ✓ {course.name}")
        print(f"    - Exam: {exam.title}")
        print(f"    - Duration: {exam.duration_minutes} minutes")
        print(f"    - Questions: {q_count}")
        print(f"    - Passing Score: {exam.passing_score}%")
        print(f"    - Max Attempts: {exam.max_attempts}")
    else:
        print(f"  ✗ {course.name} - NO EXAM CREATED")
    print()
