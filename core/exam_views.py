from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Count, Max
from django.utils import timezone
from datetime import timedelta
import json
from .models import Course, CourseAccess, CourseProgress, CourseExam, ExamAttempt, ExamAnswer, ExamQuestion, ExamViolation, Certificate, CourseScheduleItem
from django.conf import settings


@login_required
def course_detail_view(request, course_id):
    """Course detail view with exam readiness check."""
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    user = request.user
    
    # Check if user has access to this course
    access = get_object_or_404(CourseAccess, user=user, course=course, is_active=True)
    progress = access.progress if hasattr(access, '_progress') else None
    
    total_items = CourseScheduleItem.objects.filter(day__course=course, is_active=True).count()
    try:
        watched_set = set(int(x) for x in (progress.completed_lessons if progress else []))
    except Exception:
        watched_set = set()
    course_item_ids = set(CourseScheduleItem.objects.filter(day__course=course, is_active=True).values_list('id', flat=True))
    watched_items = len(course_item_ids.intersection(watched_set))
    all_watched = watched_items >= total_items and total_items > 0
    
    # Check exam eligibility
    exam = course.exam if hasattr(course, 'exam') else None
    exam_eligible = all_watched and exam and exam.is_active
    
    # Get previous attempts
    attempts = ExamAttempt.objects.filter(course_access=access).order_by('-created_at')
    passed_attempt = attempts.filter(is_passed=True).first()
    remaining_attempts = (exam.max_attempts - attempts.count()) if exam else 0
    
    context = {
        'course': course,
        'access': access,
        'progress': progress,
        'all_watched': all_watched,
        'watched_items': watched_items,
        'total_items': total_items,
        'exam': exam,
        'exam_eligible': exam_eligible,
        'attempts': attempts,
        'passed_attempt': passed_attempt,
        'remaining_attempts': remaining_attempts,
    }
    
    return render(request, 'course_detail.html', context)


@login_required
def exam_check_eligibility(request, course_id):
    """API endpoint to check exam eligibility."""
    course = get_object_or_404(Course, pk=course_id)
    access = get_object_or_404(CourseAccess, user=request.user, course=course, is_active=True)
    
    progress = access._progress if hasattr(access, '_progress') else None
    total_items = CourseScheduleItem.objects.filter(day__course=course, is_active=True).count()
    try:
        watched_set = set(int(x) for x in (progress.completed_lessons if progress else []))
    except Exception:
        watched_set = set()
    course_item_ids = set(CourseScheduleItem.objects.filter(day__course=course, is_active=True).values_list('id', flat=True))
    watched_items = len(course_item_ids.intersection(watched_set))
    all_watched = watched_items >= total_items and total_items > 0
    
    exam = course.exam if hasattr(course, 'exam') else None
    exam_eligible = all_watched and exam and exam.is_active
    
    # Check attempts — count only submitted attempts when determining attempts used
    submitted_attempts_qs = ExamAttempt.objects.filter(course_access=access, is_submitted=True)
    submitted_count = submitted_attempts_qs.count()
    passed = ExamAttempt.objects.filter(course_access=access, is_passed=True).exists()
    remaining_attempts = (exam.max_attempts - submitted_count) if exam else 0
    
    return JsonResponse({
        'eligible': exam_eligible and not passed and remaining_attempts > 0,
        'all_watched': all_watched,
        'exam_active': exam and exam.is_active,
        'remaining_attempts': max(0, remaining_attempts),
        'already_passed': passed,
        'attempts_used': submitted_count,
        'attempts_allowed': exam.max_attempts if exam else 0,
    })


@login_required
def exam_start(request, course_id):
    """Initialize exam and redirect to exam portal."""
    course = get_object_or_404(Course, pk=course_id)
    access = get_object_or_404(CourseAccess, user=request.user, course=course, is_active=True)
    exam = get_object_or_404(CourseExam, course=course, is_active=True)
    
    # Check if user already passed
    passed = ExamAttempt.objects.filter(course_access=access, is_passed=True).exists()
    if passed:
        return JsonResponse({'error': 'Already passed the exam'}, status=400)
    
    # Check for unsubmitted attempts - if one exists, redirect to it
    unsubmitted = ExamAttempt.objects.filter(
        course_access=access,
        is_submitted=False
    ).order_by('-attempt_number').first()
    
    if unsubmitted:
        # Resume the existing unsubmitted attempt
        return redirect('exam_portal', attempt_id=unsubmitted.id)
    
    # Check if user has exhausted all submitted attempts (allow resuming unsubmitted attempt)
    attempts = ExamAttempt.objects.filter(course_access=access)
    submitted_count = attempts.filter(is_submitted=True).count()
    if submitted_count >= exam.max_attempts:
        return JsonResponse({'error': 'No attempts remaining'}, status=400)
    
    # Create new attempt
    # attempt_number should be last attempt_number + 1
    last_attempt = attempts.order_by('-attempt_number').first()
    attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
    attempt = ExamAttempt.objects.create(
        course_access=access,
        attempt_number=attempt_number,
        total_questions=exam.questions.filter(is_active=True).count(),
        duration_minutes=exam.duration_minutes  # Capture exam duration at time of attempt creation
    )
    
    return redirect('exam_portal', attempt_id=attempt.id)


@login_required
def exam_portal(request, attempt_id):
    """Full-screen exam portal."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)
    exam = attempt.course_access.course.exam
    course = attempt.course_access.course
    
    if attempt.is_submitted:
        return redirect('exam_results', attempt_id=attempt.id)
    
    questions = exam.questions.filter(is_active=True).order_by('order')
    
    context = {
        'attempt': attempt,
        'exam': exam,
        'course': course,
        'questions': questions,
        'total_questions': questions.count(),
        'duration_minutes': exam.duration_minutes,
    }
    
    return render(request, 'exam_portal.html', context)


@require_http_methods(['GET'])
@login_required
def exam_get_questions(request, attempt_id):
    """API: Get all questions for the exam."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)
    exam = attempt.course_access.course.exam
    
    if attempt.is_submitted:
        return JsonResponse({'error': 'Exam already submitted'}, status=400)
    
    questions = exam.questions.filter(is_active=True).order_by('order')
    
    # Fetch user's answers
    answers = ExamAnswer.objects.filter(attempt=attempt)
    answer_map = {a.question_id: a.selected_answer for a in answers}
    
    data = []
    for q in questions:
        data.append({
            'id': q.id,
            'order': q.order,
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'selected_answer': answer_map.get(q.id, ''),
        })
    
    return JsonResponse({'questions': data, 'total': len(data)})


@require_http_methods(['GET'])
@login_required
def exam_time_left(request, attempt_id):
    """API: return remaining seconds for the attempt based on server time.

    This endpoint should be polled by the client so the timer cannot be
    arbitrarily extended on the client side. It returns remaining seconds
    (>= 0) and whether the attempt has already been submitted.
    
    Uses the attempt's stored duration (snapshot at creation time) to prevent
    admin duration changes from invalidating in-progress attempts.
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)

    # If the attempt is already submitted, remaining is zero
    if attempt.is_submitted:
        meta = {
            'exam_active': exam.is_active,
            'exam_updated_at': (exam.updated_at.isoformat() if exam.updated_at else None),
        }
        qagg = exam.questions.aggregate(updated_at=Max('updated_at'), total=Count('id'))
        meta['questions_updated_at'] = (qagg.get('updated_at').isoformat() if qagg.get('updated_at') else None)
        meta['questions_count'] = int(qagg.get('total') or 0)
        meta['duration_minutes'] = exam.duration_minutes
        return JsonResponse({'remaining_seconds': 0, 'is_submitted': True, **meta})

    # Compute elapsed seconds since attempt started
    now = timezone.now()
    elapsed = int((now - attempt.started_at).total_seconds())
    # Use the attempt's stored duration (captured at creation time), not the current exam duration
    total_seconds = (attempt.duration_minutes or 150) * 60
    remaining = max(0, total_seconds - elapsed)

    # If remaining time is 0 and attempt not submitted, finalize server-side
    if remaining <= 0 and not attempt.is_submitted:
        # mark as submitted and grade
        with transaction.atomic():
            _finalize_and_grade_attempt(attempt)
        return JsonResponse({'remaining_seconds': 0, 'is_submitted': True})

    meta = {
        'exam_active': exam.is_active,
        'exam_updated_at': (exam.updated_at.isoformat() if exam.updated_at else None),
    }
    qagg = exam.questions.aggregate(updated_at=Max('updated_at'), total=Count('id'))
    meta['questions_updated_at'] = (qagg.get('updated_at').isoformat() if qagg.get('updated_at') else None)
    meta['questions_count'] = int(qagg.get('total') or 0)
    meta['duration_minutes'] = exam.duration_minutes
    return JsonResponse({'remaining_seconds': remaining, 'is_submitted': False, **meta})


@require_http_methods(['POST'])
@login_required
def exam_save_answer(request, attempt_id):
    """API: Save user's answer to a question."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)
    
    if attempt.is_submitted:
        return JsonResponse({'error': 'Exam already submitted'}, status=400)
    
    data = json.loads(request.body)
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer', '')
    
    question = get_object_or_404(ExamQuestion, id=question_id, exam=attempt.course_access.course.exam)
    
    answer, created = ExamAnswer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={'selected_answer': selected_answer}
    )
    
    return JsonResponse({'success': True})


@require_http_methods(['POST'])
@login_required
def exam_submit(request, attempt_id):
    """API: Submit exam and auto-grade."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)
    exam = attempt.course_access.course.exam
    
    if attempt.is_submitted:
        return JsonResponse({'error': 'Already submitted'}, status=400)
    
    with transaction.atomic():
        # Finalize grading via helper (keeps logic in one place)
        result = _finalize_and_grade_attempt(attempt)
    
    return JsonResponse({
        'success': True,
        'score_percentage': float(attempt.score_percentage),
        'is_passed': attempt.is_passed,
        'correct_answers': attempt.correct_answers,
        'total_questions': result.get('total_questions', 0),
    })


def _generate_certificate_if_not_exists(course_access):
    """Generate certificate for course access if one doesn't exist."""
    course_progress = course_access._progress if hasattr(course_access, '_progress') else None
    if not course_progress:
        return
    
    if hasattr(course_progress, 'certificate'):
        return
    
    import uuid
    cert_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
    Certificate.objects.create(
        course_progress=course_progress,
        certificate_type='achievement',
        certificate_number=cert_number
    )


def _finalize_and_grade_attempt(attempt):
    """Internal helper to grade and finalize an ExamAttempt.

    Returns a dict with grading results and total questions count.
    """
    exam = attempt.course_access.course.exam
    answers = ExamAnswer.objects.filter(attempt=attempt).select_related('question')
    questions = exam.questions.filter(is_active=True)

    correct_count = 0
    for answer in answers:
        is_correct = answer.selected_answer == answer.question.correct_answer
        answer.is_correct = is_correct
        answer.save()
        if is_correct:
            correct_count += 1

    total = questions.count()
    score_percentage = (correct_count / total * 100) if total > 0 else 0
    is_passed = score_percentage >= exam.passing_score

    attempt.submitted_at = timezone.now()
    attempt.time_taken_seconds = int((attempt.submitted_at - attempt.started_at).total_seconds())
    attempt.is_submitted = True
    attempt.correct_answers = correct_count
    attempt.score_percentage = score_percentage
    attempt.is_passed = is_passed
    attempt.save()

    if is_passed:
        _generate_certificate_if_not_exists(attempt.course_access)

    return {
        'is_passed': is_passed,
        'score_percentage': score_percentage,
        'correct_count': correct_count,
        'total_questions': total,
    }


@require_http_methods(['POST'])
@login_required
def exam_record_violation(request, attempt_id):
    """API: Record a security violation during the exam."""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)
    
    if attempt.is_submitted:
        return JsonResponse({'error': 'Exam already submitted'}, status=400)
    
    data = json.loads(request.body)
    violation_type = data.get('violation_type', 'other')
    description = data.get('description', '')
    should_auto_submit = data.get('auto_submit', False)
    
    # Record the violation
    violation, created = ExamViolation.objects.update_or_create(
        attempt=attempt,
        violation_type=violation_type,
        defaults={
            'description': description,
            'auto_submitted': should_auto_submit,
            'violation_count': (ExamViolation.objects.get(attempt=attempt, violation_type=violation_type).violation_count + 1) if not created else 1,
        }
    )
    
    # Update attempt violation tracking
    attempt.has_violations = True
    attempt.violation_count = ExamViolation.objects.filter(attempt=attempt).aggregate(total=Count('id'))['total'] or 0
    attempt.save()
    
    # If auto-submit is requested, finalize the exam
    if should_auto_submit and not attempt.is_submitted:
        with transaction.atomic():
            _finalize_and_grade_attempt(attempt)
        return JsonResponse({
            'success': True,
            'auto_submitted': True,
            'message': 'Your exam has been auto-submitted due to a security violation.'
        })
    
    return JsonResponse({
        'success': True,
        'violation_recorded': True,
        'violation_type': violation_type,
    })


@login_required
def exam_results(request, attempt_id):
    """Display exam results with violation handling.
    
    If the current attempt has violations, display answers from the last valid attempt instead.
    This prevents users from easily accessing answers through violations.
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, course_access__user=request.user)
    
    if not attempt.is_submitted:
        return redirect('exam_portal', attempt_id=attempt.id)
    
    exam = attempt.course_access.course.exam
    violations = ExamViolation.objects.filter(attempt=attempt)
    has_violations = attempt.has_violations and violations.exists()
    
    # Determine which attempt to show answers from
    display_attempt = attempt
    if has_violations:
        # If current attempt has violations, find the last valid (non-violated) submitted attempt
        last_valid = ExamAttempt.objects.filter(
            course_access=attempt.course_access,
            is_submitted=True,
            has_violations=False,
            attempt_number__lt=attempt.attempt_number
        ).order_by('-attempt_number').first()
        
        if last_valid:
            display_attempt = last_valid
    
    # Get answers to display
    answers = ExamAnswer.objects.filter(attempt=display_attempt).select_related('question')
    
    # Build answer detail
    answer_details = []
    for ans in answers:
        answer_details.append({
            'question': ans.question,
            'selected': ans.selected_answer,
            'correct': ans.question.correct_answer,
            'is_correct': ans.is_correct,
            'explanation': ans.question.explanation,
        })
    
    context = {
        'attempt': attempt,
        'display_attempt': display_attempt,
        'exam': exam,
        'answer_details': answer_details,
        'passed': attempt.is_passed,
        'violations': violations,
        'has_violations': has_violations,
        'showing_previous_attempt': display_attempt.id != attempt.id,
    }
    
    return render(request, 'exam_results.html', context)


@login_required
def exam_remind_later(request, course_id):
    """User chooses to take exam later; redirect to course."""
    course = get_object_or_404(Course, pk=course_id)
    return redirect('course_detail', slug=course.slug)
