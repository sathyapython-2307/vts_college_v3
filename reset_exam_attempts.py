#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CourseAccess, ExamAttempt, Course

# Find user u2@gmail.com
user = User.objects.filter(username='u2@gmail.com').first()
if not user:
    print("User u2@gmail.com not found")
    exit(1)

print(f"Found user: {user.email}")

# Find all exam attempts for this user
attempts = ExamAttempt.objects.filter(course_access__user=user)
count = attempts.count()
print(f"Found {count} exam attempts")

# Delete them
attempts.delete()
print(f"Deleted {count} exam attempts")

# List remaining courses for this user
accesses = CourseAccess.objects.filter(user=user, is_active=True)
print(f"\nUser now has {accesses.count()} active course accesses:")
for access in accesses:
    print(f"  - {access.course.name}")
