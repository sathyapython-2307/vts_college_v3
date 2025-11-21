from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db.models import Q
from core.models import CourseAccess, ExamAttempt, ExamAnswer


class Command(BaseCommand):
    help = 'Reset (delete) all exam attempts for a given user email/username.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='User email (or username) to reset attempts for')
        parser.add_argument('--course_id', type=int, default=None, help='Optional course id to limit reset')

    def handle(self, *args, **options):
        email = options['email']
        course_id = options.get('course_id')
        User = get_user_model()

        user = User.objects.filter(Q(email=email) | Q(username=email)).first()
        if not user:
            raise CommandError(f'User not found for "{email}"')

        accesses = CourseAccess.objects.filter(user=user)
        if course_id:
            accesses = accesses.filter(course_id=course_id)

        if not accesses.exists():
            self.stdout.write(self.style.WARNING('No course accesses found for user.'))
            return

        total_attempts = 0
        total_answers = 0
        for access in accesses:
            attempts = ExamAttempt.objects.filter(course_access=access)
            answers = ExamAnswer.objects.filter(attempt__in=attempts)
            count_attempts = attempts.count()
            count_answers = answers.count()

            # Delete answers first, then attempts
            answers.delete()
            attempts.delete()

            total_attempts += count_attempts
            total_answers += count_answers

        self.stdout.write(self.style.SUCCESS(
            f'Reset completed for {email}: removed {total_attempts} attempts and {total_answers} answers' +
            (f' (course_id={course_id})' if course_id else '')
        ))