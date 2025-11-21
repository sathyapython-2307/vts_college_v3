from django.core.management.base import BaseCommand
from core.models import Course, CourseExam, ExamQuestion


class Command(BaseCommand):
    help = 'Seed 150 MCQ questions for a specific course exam'

    def add_arguments(self, parser):
        parser.add_argument(
            'course_id',
            type=int,
            help='The ID of the course to create an exam for'
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=180,
            help='Exam duration in minutes (default: 180)'
        )
        parser.add_argument(
            '--passing-score',
            type=int,
            default=80,
            help='Passing score percentage (default: 80)'
        )
        parser.add_argument(
            '--max-attempts',
            type=int,
            default=3,
            help='Maximum attempts allowed (default: 3)'
        )

    def handle(self, *args, **options):
        course_id = options['course_id']
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Course with ID {course_id} not found'))
            return
        
        # Create or get CourseExam
        course_exam, created = CourseExam.objects.get_or_create(
            course=course,
            defaults={
                'title': f'{course.name} Certification Exam',
                'duration_minutes': options['duration'],
                'passing_score': options['passing_score'],
                'max_attempts': options['max_attempts'],
                'is_active': True,
            }
        )
        
        if not created:
            self.stdout.write(self.style.WARNING(f'Exam already exists for {course.name}'))
            # Update the exam settings
            course_exam.duration_minutes = options['duration']
            course_exam.passing_score = options['passing_score']
            course_exam.max_attempts = options['max_attempts']
            course_exam.save()
            self.stdout.write(self.style.SUCCESS(f'Updated exam settings for {course.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created exam for {course.name}'))
        
        # Sample MCQ questions data
        questions_data = [
            {
                'question_text': 'What is the purpose of this course?',
                'option_a': 'To teach fundamental concepts',
                'option_b': 'To provide entertainment only',
                'option_c': 'To waste time',
                'option_d': 'To confuse learners',
                'correct_answer': 'A',
                'explanation': 'This course is designed to teach fundamental concepts and skills to learners.',
            },
            {
                'question_text': 'Which of the following is a key learning outcome?',
                'option_a': 'Ability to apply concepts in real-world scenarios',
                'option_b': 'Ability to memorize without understanding',
                'option_c': 'Ability to copy-paste code',
                'option_d': 'Ability to ignore best practices',
                'correct_answer': 'A',
                'explanation': 'The key learning outcome is the ability to apply what you have learned to solve real-world problems.',
            },
            {
                'question_text': 'What is the recommended study approach?',
                'option_a': 'Watch videos and take notes',
                'option_b': 'Skip through content',
                'option_c': 'Only read the description',
                'option_d': 'Ask for answers',
                'correct_answer': 'A',
                'explanation': 'The recommended approach is to actively engage with the material by watching videos carefully and taking comprehensive notes.',
            },
            {
                'question_text': 'How many attempts are allowed for the final exam?',
                'option_a': 'Unlimited',
                'option_b': '3 attempts',
                'option_c': '1 attempt only',
                'option_d': '10 attempts',
                'correct_answer': 'B',
                'explanation': f'You are allowed up to {options["max_attempts"]} attempts to complete the exam.',
            },
            {
                'question_text': 'What is the passing score requirement?',
                'option_a': '50%',
                'option_b': '60%',
                'option_c': '80%',
                'option_d': '90%',
                'correct_answer': 'C',
                'explanation': f'You need to score at least {options["passing_score"]}% to pass the exam and earn the certificate.',
            },
        ]
        
        # Generate 150 questions by repeating and varying the sample questions
        all_questions = []
        for i in range(150):
            base_question = questions_data[i % len(questions_data)]
            question = ExamQuestion(
                exam=course_exam,
                question_text=f'{base_question["question_text"]} (Question {i+1})',
                option_a=base_question['option_a'],
                option_b=base_question['option_b'],
                option_c=base_question['option_c'],
                option_d=base_question['option_d'],
                correct_answer=base_question['correct_answer'],
                explanation=base_question['explanation'],
                order=i + 1,
                is_active=True,
            )
            all_questions.append(question)
        
        # Bulk create questions
        ExamQuestion.objects.filter(exam=course_exam).delete()
        ExamQuestion.objects.bulk_create(all_questions)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created 150 exam questions for course "{course.name}"'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Exam settings: Duration={options["duration"]}min, '
            f'Passing Score={options["passing_score"]}%, Max Attempts={options["max_attempts"]}'
        ))
