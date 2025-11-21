#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from core.models import Course, CourseExam, ExamQuestion
from django.db import transaction

# Get all active courses
courses = Course.objects.filter(is_active=True)
print("Creating exams for courses without them...\n")

created_exams = 0
created_questions = 0

for course in courses:
    exam = CourseExam.objects.filter(course=course, is_active=True).first()
    
    if exam:
        # Exam already exists, skip
        continue
    
    # Create exam with same config as UI/UX
    with transaction.atomic():
        exam = CourseExam.objects.create(
            course=course,
            title=f"{course.name} Certification Exam",
            description=f"Comprehensive certification exam for {course.name}",
            duration_minutes=150,  # Same 2.5 hours as UI/UX
            passing_score=80,       # Same 80% as UI/UX
            max_attempts=3,         # Same 3 attempts as UI/UX
            is_active=True
        )
        created_exams += 1
        print(f"✓ Created exam for: {course.name}")

        # Create 150 sample questions (same count as UI/UX)
        for i in range(1, 151):
            topic_area = [
                "Core Concepts",
                "Advanced Techniques",
                "Best Practices",
                "Real-World Applications",
                "Performance Optimization"
            ][i % 5]

            ExamQuestion.objects.create(
                exam=exam,
                order=i,
                question_text=f"Question {i}: What is your understanding of {topic_area.lower()} in {course.name}?",
                option_a=f"This is a fundamental aspect of {topic_area}",
                option_b=f"This relates to intermediate knowledge in {topic_area}",
                option_c=f"This is an advanced concept in {topic_area}",
                option_d=f"This is a specialized skill in {topic_area}",
                correct_answer='A' if i % 4 == 1 else ('B' if i % 4 == 2 else ('C' if i % 4 == 3 else 'D')),
                explanation=f"This question tests understanding of {topic_area} concepts in {course.name}.",
                is_active=True
            )
            created_questions += 1
            
            if i % 30 == 0:
                print(f"  → Created {i}/150 questions")

print(f"\n✅ Summary:")
print(f"  - Exams Created: {created_exams}")
print(f"  - Questions Created: {created_questions}")
print(f"  - Total Questions per Exam: 150")
print(f"  - Duration per Exam: 150 minutes")
print(f"  - Passing Score: 80%")
print(f"  - Max Attempts: 3")
