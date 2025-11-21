#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from core.models import Course, CourseExam

# Find UI UX Designing course
course = Course.objects.filter(name__icontains='UI UX').first()
if not course:
    print("Course not found")
    exit(1)

print(f"Course: {course.name}")

# Check exam
exam = CourseExam.objects.filter(course=course).first()
if exam:
    print(f"Exam: {exam.title}")
    print(f"Duration: {exam.duration_minutes} minutes")
    print(f"Passing Score: {exam.passing_score}%")
    print(f"Max Attempts: {exam.max_attempts}")
    print(f"Questions: {exam.questions.filter(is_active=True).count()}")
else:
    print("No exam found for this course")
