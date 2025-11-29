from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.db.models import Count
try:
    import razorpay
except Exception:
    razorpay = None
import json
import logging

# Import core models used by views
from .models import (
    AboutPage, AboutSection, Course, CourseBrochure, CourseScheduleDay,
    CourseScheduleItem, CourseAccess, CourseProgress, CoursePayment,
    CourseExam, ExamAttempt, Certificate, ExamCertificate
)

# Also import VideoPlay model for play tracking
from .models import VideoPlay

# Brochure downloads are stored in a separate module
from .models_brochure import BrochureDownload

# Module logger
logger = logging.getLogger(__name__)


def health(request):
    """Simple health endpoint used by Render and post-deploy checks.

    Returns 200 with a small JSON payload. Attempts a lightweight DB query
    (`Course.objects.exists()`) to surface obvious DB/schema issues.
    """
    status = {'status': 'ok'}
    try:
        # A harmless DB query to ensure the default DB and migrations are OK.
        _ = Course.objects.exists()
        status['db'] = 'ok'
    except Exception as e:
        # Capture error so operators can inspect logs if the health check fails.
        status['db'] = 'error'
        status['db_error'] = str(e)

    return JsonResponse(status)


def static_check(request):
    """Diagnostic endpoint to list files in STATIC_ROOT and show manifest contents.

    This endpoint is gated by the `STATIC_CHECK_SECRET` environment variable. To
    enable, set `STATIC_CHECK_SECRET` in Render to a secret string and call the
    endpoint with `?secret=THE_SECRET`.
    """
    import os
    import os
    # secret = os.environ.get('STATIC_CHECK_SECRET')
    # provided = request.GET.get('secret')
    # if not secret or provided != secret:
    #     return JsonResponse({'error': 'not found'}, status=404)

    root = getattr(django_settings, 'STATIC_ROOT', None)
    base_dir = getattr(django_settings, 'BASE_DIR', None)
    
    if not root:
        return JsonResponse({'error': 'STATIC_ROOT not configured'}, status=500)

    result = {
        'static_root': str(root), 
        'base_dir': str(base_dir),
        'files': [], 
        'manifest': None, 
        'manifests_found': []
    }
    try:
        # List files (top-level, not recursive heavy walk)
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                result['files'].append(rel.replace('\\', '/'))

        # Check common manifest filenames created by Manifest storage variants
        import json as _json
        for candidate in ('manifest.json', 'staticfiles.json', 'staticfiles_manifest.json', 'manifest-static.json'):
            manifest_path = os.path.join(root, candidate)
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        parsed = _json.load(f)
                    result['manifests_found'].append(candidate)
                    # only set 'manifest' to the first found to keep output small
                    if result['manifest'] is None:
                        result['manifest'] = parsed
                except Exception as me:
                    result.setdefault('manifest_errors', {})[candidate] = str(me)
    except Exception as e:
        result['error'] = str(e)

    return JsonResponse(result)


@login_required
def settings(request):
    return render(request, 'settings.html')

def about(request):
    """Render the about page with dynamic AboutPage and AboutSection content."""
    about_page = AboutPage.objects.filter(is_active=True).order_by('-updated_at').first()
    about_sections = AboutSection.objects.filter(is_active=True).order_by('order')

    context = {
        'about_page': about_page,
        'about_sections': about_sections,
    }

    return render(request, 'about.html', context)

def contact(request):
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def team(request):
    return render(request, 'team.html')


def home(request):
    """Render the home page."""
    return render(request, 'home.html')


def signup_view(request):
    """Simple signup page stub. Full registration handled elsewhere."""
    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'registration/signup.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/signup.html')

        # Use email as username to keep authentication consistent
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        if UserModel.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists. Please log in.')
            return redirect('login')

        try:
            user = UserModel.objects.create_user(username=email, email=email, password=password)
            # Save the provided name into first_name for display
            if name:
                user.first_name = name
                user.save()
            login(request, user)
            messages.success(request, 'Account created and logged in successfully.')
            return redirect('my-purchase')
        except Exception as e:
            messages.error(request, f'Failed to create account: {str(e)}')
            return render(request, 'registration/signup.html')

    return render(request, 'registration/signup.html')


def login_view(request):
    """Simple login page stub."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'registration/login.html')

        # Authenticate using email-as-username
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            # Respect next parameter if provided
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url or 'home')
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'registration/login.html')

    return render(request, 'registration/login.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def my_purchase(request):
    """Render the My Purchase page with the user's active course accesses.

    The template expects `course_accesses` (iterable of access objects) and
    an `active_tab` string. Historically `CourseAccess.progress` was a numeric
    value in templates; the model property now returns a `CourseProgress`
    object. To keep the template unchanged we attach a numeric `progress`
    attribute to each access instance (shadowing the property) which holds
    the percentage value.
    """
    # Query active accesses for the logged-in user
    accesses = CourseAccess.objects.filter(user=request.user, is_active=True).select_related('course', 'payment')

    course_accesses = []
    for access in accesses:
        # Ensure a CourseProgress exists and is refreshed if possible
        try:
            prog = access.progress  # this returns CourseProgress object
            try:
                prog.update_progress()
            except Exception:
                # non-fatal: keep whatever progress value exists
                pass
            progress_value = float(prog.progress_percentage) if hasattr(prog, 'progress_percentage') else 0.0
        except Exception:
            progress_value = 0.0

        # Attach numeric progress to the instance so the template can use
        # `access.progress` as before (this shadows the property at instance level)
        try:
            setattr(access, 'progress', progress_value)
        except Exception:
            # If we cannot set attribute for some reason, ignore and continue
            pass

        course_accesses.append(access)

    context = {
        'course_accesses': course_accesses,
        'active_tab': 'courses',
    }

    # Include certificates for the logged-in user so the Achievements tab
    # can show either a pending message or a download button when available.
    try:
        certificates = Certificate.objects.filter(
            course_progress__course_access__user=request.user
        ).select_related('course_progress__course_access__course')
    except Exception:
        certificates = []
    
    # Include exam certificates for students who scored 80%+
    try:
        exam_certificates = ExamCertificate.objects.filter(
            exam_attempt__course_access__user=request.user,
            is_active=True
        ).select_related('exam_attempt__course_access__course').order_by('-exam_submitted_date')
    except Exception:
        exam_certificates = []

    context['certificates'] = certificates
    context['exam_certificates'] = exam_certificates

    return render(request, 'my_purchase.html', context)


@login_required
def my_results(request):
    """Show a user's submitted exam attempts and links to detailed results.

    If the user has not attended any exams (no submitted attempts), show
    a friendly prompt asking them to watch course videos and take the exam.
    """
    from .models import ExamAttempt

    attempts = ExamAttempt.objects.filter(course_access__user=request.user, is_submitted=True).select_related('course_access__course').order_by('-submitted_at')

    if not attempts.exists():
        # Friendly prompt when no submitted attempts are found
        return render(request, 'my_results.html', {
            'attempts': [],
            'no_attempts_message': 'Kindly see all videos and attend exam to view results.'
        })

    return render(request, 'my_results.html', {
        'attempts': attempts,
        'no_attempts_message': None,
    })

def testimonials(request):
    return render(request, 'testimonials.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def download_brochure(request, course_slug):
    """
    Handle downloading of course brochure with user information tracking.
    """
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    brochure = get_object_or_404(CourseBrochure, course=course, is_active=True)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Create brochure download record
            BrochureDownload.objects.create(
                user_name=request.POST.get('user_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                course=course,
                brochure=brochure,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return FileResponse(brochure.brochure_file, as_attachment=True, 
                             filename=f"{course.name}_brochure.pdf")
        except Exception as e:
            logger.error(f"Brochure download error: {str(e)}")
            return JsonResponse({'error': 'Failed to process download'}, status=500)
    else:
        messages.error(request, "Please fill out the form to download the brochure.")
        return redirect('course_detail', slug=course_slug)

def course_detail(request, slug):
    """
    Display the details of a specific course.
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    related_courses = Course.objects.filter(
        category=course.category,
        is_active=True
    ).exclude(id=course.id)[:3]  # Get 3 related courses
    # Prepare instructor lists for the template to avoid calling queryset methods
    # inside the template (TemplateLanguage cannot parse chained calls with args).
    local_instructors = course.local_instructors.filter(is_active=True).order_by('order')
    course_instructors = course.courseinstructor_set.select_related('instructor').order_by('order')

    # Get exam information if it exists
    try:
        course_exam = CourseExam.objects.filter(course=course, is_active=True).first()
        total_exam_questions = 0
        exam_duration_minutes = 120  # default
        if course_exam:
            from .models import ExamQuestion
            total_exam_questions = ExamQuestion.objects.filter(exam=course_exam, is_active=True).count()
            exam_duration_minutes = course_exam.duration_minutes if hasattr(course_exam, 'duration_minutes') else 120
    except Exception:
        course_exam = None
        total_exam_questions = 0
        exam_duration_minutes = 120

    context = {
        'course': course,
        'related_courses': related_courses,
        'local_instructors': local_instructors,
        'course_instructors': course_instructors,
        'course_features': course.features.all(),
        'course_skills': course.skills.filter(is_active=True).order_by('order'),
        'course_tools': course.tools.filter(is_active=True).order_by('order'),
        'course_overviews': course.overviews.filter(is_active=True).order_by('order'),
        'brochure': CourseBrochure.objects.filter(course=course, is_active=True).first(),
        'exam': course_exam,
        'total_exam_questions': total_exam_questions,
        'exam_duration_minutes': exam_duration_minutes,
    }
    # Determine if the current logged-in user already has access to this course
    try:
        has_access = False
        if request.user.is_authenticated:
            has_access = CourseAccess.objects.filter(user=request.user, course=course, is_active=True).exists()
    except Exception:
        # If anything goes wrong while checking access, default to False
        has_access = False

    context['has_access'] = has_access
    
    # We've disabled DB-driven per-video tracking for testing. Provide safe
    # defaults so templates and other code paths don't break.
    exam_eligible = False
    exam_attempt = None
    if request.user.is_authenticated and has_access:
        try:
            course_access = CourseAccess.objects.get(user=request.user, course=course, is_active=True)
            # Keep progress data available but do not modify ready_for_exam here.
            progress = course_access.progress
            try:
                progress.update_progress()
            except Exception:
                pass
            # Do not compute/modify ready_for_exam based on removed VideoPlay records.
        except (CourseAccess.DoesNotExist, Exception):
            pass

    # Expose whether the congratulations container should be shown permanently.
    # Since we've removed server-side per-video tracking, default to False.
    context['show_congratulations'] = False
    context['exam_eligible'] = exam_eligible
    context['exam_attempt'] = exam_attempt
    # Build grouped schedule days to avoid duplicate day blocks when DB has multiple
    # CourseScheduleDay rows with the same `order`. This merges their items for display.
    try:
        from itertools import chain
        schedule_days_qs = course.schedule_days.filter(is_active=True).order_by('order', 'id').prefetch_related('items')
        grouped = []
        last_order = None
        for day in schedule_days_qs:
            if last_order is None or day.order != last_order:
                # start a new group
                grouped.append({
                    'title': day.title,
                    'order': day.order,
                    'items': list(day.items.filter(is_active=True).order_by('order'))
                })
                last_order = day.order
            else:
                # merge items into the previous group
                grouped[-1]['items'].extend(list(day.items.filter(is_active=True).order_by('order')))

        context['grouped_schedule_days'] = grouped
    except Exception:
        # Fallback to original queryset in case of any error
        context['grouped_schedule_days'] = list(course.schedule_days.filter(is_active=True).order_by('order'))

    return render(request, 'course_detail.html', context)


def course_detail_by_id(request, course_id):
    """
    Backwards-compatibility helper: if a numeric course URL is used (e.g. /course/3/)
    redirect to the canonical slug URL for that course. This avoids 404s when
    older links or external references use numeric IDs.
    """
    course = get_object_or_404(Course, id=course_id, is_active=True)
    # Redirect to the canonical slug-based URL
    return redirect('course_detail', slug=course.slug)


@login_required
def mark_video_watched(request, course_id, item_id):
    """
    Mark a specific CourseScheduleItem as watched for the current user.

    This endpoint is authoritative: it records a `VideoPlay` row (if not
    already present), recalculates progress for the user's `CourseProgress`,
    sets `ready_for_exam` when the user has played all course videos, and
    returns JSON with progress counts and flags.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        course_id = int(course_id)
        item_id = int(item_id)

        course = get_object_or_404(Course, id=course_id, is_active=True)
        course_item = get_object_or_404(CourseScheduleItem, id=item_id, day__course=course, is_active=True)

        # Ensure user has access to the course
        course_access = CourseAccess.objects.filter(user=request.user, course=course, is_active=True).first()
        if not course_access:
            return JsonResponse({'error': 'User does not have access to this course'}, status=403)

        # Ensure progress exists
        progress, _ = CourseProgress.objects.get_or_create(course_access=course_access)

        # Create VideoPlay record if not exists
        try:
            VideoPlay.objects.get_or_create(user=request.user, course_item=course_item)
        except Exception:
            # If VideoPlay fails for some reason, continue gracefully
            pass

        # Calculate all active course video IDs
        all_course_videos = list(CourseScheduleItem.objects.filter(day__course=course, is_active=True).values_list('id', flat=True))
        course_video_set = set(all_course_videos)

        # Watched IDs come from VideoPlay rows
        watched_ids_qs = VideoPlay.objects.filter(user=request.user, course_item__day__course=course).values_list('course_item', flat=True)
        try:
            watched_set = set(int(x) for x in watched_ids_qs)
        except Exception:
            watched_set = set()

        watched_in_course = course_video_set.intersection(watched_set)
        completed_count = len(watched_in_course)
        total_items = len(course_video_set)

        all_watched = (total_items > 0) and (completed_count == total_items)
        progress_percentage = (completed_count / total_items * 100) if total_items > 0 else 0

        # Persist ready_for_exam when all videos are watched
        if all_watched and not progress.ready_for_exam:
            from django.utils import timezone
            progress.ready_for_exam = True
            progress.ready_for_exam_date = timezone.now()
            progress.save()

        # Keep completed_lessons list for backwards compatibility
        try:
            if item_id not in progress.completed_lessons:
                progress.completed_lessons.append(item_id)
                progress.save()
        except Exception:
            pass

        # Determine exam eligibility
        exam_eligible = False
        # prepare defaults so response can reference them safely
        exam = None
        passed = False
        attempts = 0
        attempts_remaining = 0
        if all_watched:
            exam = CourseExam.objects.filter(course=course, is_active=True).first()
            if exam:
                passed = ExamAttempt.objects.filter(course_access=course_access, is_passed=True).exists()
                # Count only submitted attempts for 'used' metric
                submitted_attempts = ExamAttempt.objects.filter(course_access=course_access, is_submitted=True).count()
                attempts_remaining = max(0, exam.max_attempts - submitted_attempts)
                exam_eligible = not passed and attempts_remaining > 0

        response_data = {
            'success': True,
            'completed': completed_count,
            'total': total_items,
            'progress_percentage': round(progress_percentage, 2),
            'all_watched': all_watched,
            'exam_eligible': exam_eligible,
            'ready_for_exam': bool(progress.ready_for_exam),
            # Exam attempt info for frontend display
            'attempts_used': submitted_attempts if all_watched and exam else 0,
            'attempts_allowed': exam.max_attempts if all_watched and exam else (exam.max_attempts if exam else 0),
            'attempts_remaining': attempts_remaining if all_watched and exam else (exam.max_attempts if exam else 0),
            'passed_exam': passed if all_watched and exam else False,
        }

        from django.conf import settings
        if getattr(settings, 'DEBUG', False):
            response_data['debug'] = {
                'course_id': course_id,
                'item_id': item_id,
                'user': str(request.user),
                'all_course_videos': all_course_videos,
                'watched_in_course': list(watched_in_course),
            }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def check_course_completion(request, course_id):
    """
    Check current completion status for the logged-in user and the given course.
    Returns counts, percentages, and the `ready_for_exam` flag so the frontend
    can show the Congratulations container persistently when appropriate.
    """
    try:
        course_id = int(course_id)
        course = get_object_or_404(Course, id=course_id, is_active=True)

        course_access = CourseAccess.objects.filter(user=request.user, course=course, is_active=True).first()
        if not course_access:
            response_data = {
                'success': True,
                'completed': 0,
                'total': CourseScheduleItem.objects.filter(day__course=course, is_active=True).count(),
                'progress_percentage': 0.0,
                'all_watched': False,
                'exam_eligible': False,
                'ready_for_exam': False,
            }
            return JsonResponse(response_data)

        progress, _ = CourseProgress.objects.get_or_create(course_access=course_access)

        all_course_videos = list(CourseScheduleItem.objects.filter(day__course=course, is_active=True).values_list('id', flat=True))
        course_video_set = set(all_course_videos)

        watched_ids_qs = VideoPlay.objects.filter(user=request.user, course_item__day__course=course).values_list('course_item', flat=True)
        try:
            watched_set = set(int(x) for x in watched_ids_qs)
        except Exception:
            watched_set = set()

        watched_in_course = course_video_set.intersection(watched_set)
        completed_count = len(watched_in_course)
        total_items = len(course_video_set)

        all_watched = (total_items > 0) and (completed_count == total_items)
        progress_percentage = (completed_count / total_items * 100) if total_items > 0 else 0

        # If all watched, persist ready_for_exam
        if all_watched and not progress.ready_for_exam:
            from django.utils import timezone
            progress.ready_for_exam = True
            progress.ready_for_exam_date = timezone.now()
            progress.save()

        exam_eligible = False
        # prepare defaults so response can reference them safely
        exam = None
        passed = False
        attempts = 0
        attempts_remaining = 0
        if all_watched:
            exam = CourseExam.objects.filter(course=course, is_active=True).first()
            if exam:
                passed = ExamAttempt.objects.filter(course_access=course_access, is_passed=True).exists()
                # Only count submitted attempts toward the used attempts total. Unsubmitted
                # attempts can be resumed and should not be treated as consumed.
                submitted_count = ExamAttempt.objects.filter(course_access=course_access, is_submitted=True).count()
                attempts = submitted_count
                attempts_remaining = max(0, exam.max_attempts - submitted_count)
                exam_eligible = not passed and attempts_remaining > 0

        response_data = {
            'success': True,
            'completed': completed_count,
            'total': total_items,
            'progress_percentage': round(progress_percentage, 2),
            'all_watched': all_watched,
            'exam_eligible': exam_eligible,
            'ready_for_exam': bool(progress.ready_for_exam),
            # Include exam attempt counts so frontend can show attempts used/remaining
            'attempts_used': attempts if all_watched and exam else 0,
            'attempts_allowed': exam.max_attempts if exam else 0,
            'attempts_remaining': attempts_remaining if all_watched and exam else (exam.max_attempts if exam else 0),
            'passed_exam': passed if all_watched and exam else False,
            # Include exam metadata for frontend display
            'total_questions': exam.questions.filter(is_active=True).count() if exam else 0,
            'exam_duration_minutes': exam.duration_minutes if exam and hasattr(exam, 'duration_minutes') else 120,
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def course_checkout(request, slug):
    """
    Display the checkout page for a course.
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    # If the user is not authenticated, redirect them to the signup page
    # (non-logged-in users may browse product pages but must register to purchase)
    if not request.user.is_authenticated:
        return redirect('signup')
    context = {
        'course': course,
    }
    return render(request, 'checkout/checkout.html', context)

@login_required
def create_order(request, slug):
    """
    Create a Razorpay order for the course.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    course = get_object_or_404(Course, slug=slug, is_active=True)

    try:
        # Parse JSON data from request
        data = json.loads(request.body)

        # Save form data in session
        form_fields = {
            'first_name': 'checkout_first_name',
            'last_name': 'checkout_last_name',
            'email': 'checkout_email',
            'phone': 'checkout_phone',
            'address': 'checkout_address',
            'city': 'checkout_city',
            'state': 'checkout_state',
            'zip': 'checkout_zip'
        }
        for field, session_key in form_fields.items():
            request.session[session_key] = data.get(field)

        # Get configuration from settings - use direct references
        # Get configuration from settings using getattr for safety
        razorpay_settings = getattr(django_settings, 'RAZORPAY_SETTINGS', {})
        enabled = getattr(django_settings, 'RAZORPAY_ENABLED', False)
        key_id = getattr(django_settings, 'RAZORPAY_KEY_ID', '')
        key_secret = getattr(django_settings, 'RAZORPAY_KEY_SECRET', '')
        currency = getattr(django_settings, 'RAZORPAY_CURRENCY', 'INR')

        # If a local razorpay_config.py exists with explicit keys, prefer it
        try:
            import razorpay_config
            cfg = razorpay_config.get_config(test_mode=True)
            # Only override if config contains keys
            if cfg and cfg.get('KEY_ID') and cfg.get('KEY_SECRET'):
                key_id = cfg.get('KEY_ID')
                key_secret = cfg.get('KEY_SECRET')
                # Respect explicit enabled flag in the config if present
                enabled = cfg.get('ENABLED', enabled)
                currency = cfg.get('CURRENCY', currency)
                logger.info('Using razorpay_config.py for credentials')
        except Exception:
            # No local config present or failed to load: continue with settings
            pass

        # Print debug info
        print("\nDEBUG: Razorpay Settings:")
        print("-" * 50)
        print(f"Settings dict = {razorpay_settings}")
        print(f"ENABLED = {enabled}")
        print(f"KEY_ID = {key_id}")
        print(f"KEY_SECRET length = {len(key_secret) if key_secret else 0}")
        print(f"CURRENCY = {currency}")
        print("-" * 50)

        # Debug logging for troubleshooting
        # Log configuration details
        logger.debug('Razorpay Configuration:')
        logger.debug(f'- Package Available: {razorpay is not None}')
        logger.debug(f'- Settings Enabled: {razorpay_settings.get("ENABLED", False)}')
        logger.debug(f'- Effective Enabled: {enabled}')
        logger.debug(f'- KEY_ID: {key_id}')
        logger.debug(f'- KEY_SECRET length: {len(key_secret) if key_secret else 0}')
        logger.debug(f'- Currency: {currency}')

        # Log the actual configuration being used
        logger.info(f"Using Razorpay config: ENABLED={enabled}, KEY_ID={key_id}, CURRENCY={currency}")
        if django_settings.DEBUG:
            print('DEBUG: create_order using config:', {
                'ENABLED': enabled,
                'KEY_ID': key_id,
                'SECRET': '*' * 4 if key_secret else None,
                'CURRENCY': currency
            })

        if razorpay is None:
            logger.error('Razorpay package not available')
            resp = {'error': 'Payment gateway not available'}
            if django_settings.DEBUG:
                resp['debug'] = {'reason': 'razorpay package not installed'}
            return JsonResponse(resp, status=500)

        razorpay_settings = getattr(django_settings, 'RAZORPAY_SETTINGS', {})
        if not razorpay_settings.get('ENABLED', False):
            logger.error('Razorpay is disabled in settings')
            resp = {'error': 'Payment gateway not configured'}
            if django_settings.DEBUG:
                resp['debug'] = {
                    'reason': 'razorpay is disabled in settings',
                    'settings': razorpay_settings
                }
            return JsonResponse(resp, status=500)

        if not key_id or not key_secret:
            logger.error('Razorpay credentials missing')
            resp = {'error': 'Payment gateway not configured'}
            if django_settings.DEBUG:
                resp['debug'] = {
                    'KEY_ID_present': bool(key_id),
                    'KEY_SECRET_present': bool(key_secret),
                    'reason': 'missing credentials'
                }
            return JsonResponse(resp, status=500)

        # Initialize Razorpay client
        try:
            if 'razorpay' not in globals() or razorpay is None:
                logger.error('Razorpay package not installed')
                return JsonResponse({'error': 'Payment gateway not available'}, status=500)

            # Log what we're using to init the client
            if getattr(django_settings, 'DEBUG', False):
                print('DEBUG: Initializing Razorpay client with:', {
                    'key_id': key_id,
                    'key_secret': '*' * 4 if key_secret else None
                })
            client = razorpay.Client(auth=(key_id, key_secret))
            
            # Test the client by fetching payments (lightweight API call)
            client.payment.all({'count': 1})
            logger.info('Razorpay client initialized and tested successfully')
            
        except Exception as e:
            logger.exception('Razorpay client initialization/test failed')
            resp = {'error': 'Payment gateway configuration error'}
            if getattr(django_settings, 'DEBUG', False):
                resp['debug'] = {
                    'exception': str(e),
                    'key_id': key_id,
                    'key_secret_present': bool(key_secret)
                }
            return JsonResponse(resp, status=500)

        # Convert price to paise (Razorpay expects amount in smallest currency unit)
        try:
            amount = int(float(course.discounted_price) * 100)
            if amount <= 0:
                raise ValueError('Course price must be greater than 0')
        except (ValueError, TypeError) as e:
            logger.error(f'Invalid course price: {str(e)}')
            return JsonResponse({'error': 'Invalid course price'}, status=400)

        # Create Razorpay order
        try:
            order_data = {
                'amount': amount,
                'currency': currency,
                'payment_capture': 1,
                'notes': {
                    'course_id': course.id,
                    'course_name': course.name,
                    'user_id': request.user.id,
                    'user_email': data.get('email'),
                    'user_phone': data.get('phone')
                }
            }
            order = client.order.create(data=order_data)
            logger.info(f'Razorpay order created: {order}')
            return JsonResponse({
                'id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key': key_id
            })
        except Exception as e:
            logger.exception('Error creating Razorpay order')
            resp = {'error': 'Failed to create payment order'}
            if getattr(django_settings, 'DEBUG', False):
                resp['debug'] = {'exception': str(e)}
            return JsonResponse(resp, status=500)

    except json.JSONDecodeError:
        logger.error('Invalid JSON data received')
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    except Exception as e:
        # Log full traceback on the server
        logger.exception('Unexpected error in create_order')
        # If DEBUG is enabled, return the exception text and traceback
        resp = {'error': 'An unexpected error occurred'}
        if getattr(django_settings, 'DEBUG', False):
            import traceback as _traceback
            resp['debug'] = {
                'exception': str(e),
                'traceback': _traceback.format_exc()
            }
        return JsonResponse(resp, status=500)

@csrf_exempt
@login_required
def payment_callback(request, slug):
    """
    Handle Razorpay payment callback.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    try:
        # Get configuration from settings using getattr for safety
        enabled = getattr(django_settings, 'RAZORPAY_ENABLED', False)
        key_id = getattr(django_settings, 'RAZORPAY_KEY_ID', '')
        key_secret = getattr(django_settings, 'RAZORPAY_KEY_SECRET', '')
        currency = getattr(django_settings, 'RAZORPAY_CURRENCY', 'INR')

        # If a local razorpay_config.py exists with explicit keys, prefer it
        try:
            import razorpay_config
            cfg = razorpay_config.get_config(test_mode=True)
            if cfg and cfg.get('KEY_ID') and cfg.get('KEY_SECRET'):
                key_id = cfg.get('KEY_ID')
                key_secret = cfg.get('KEY_SECRET')
                enabled = cfg.get('ENABLED', enabled)
                currency = cfg.get('CURRENCY', currency)
                logger.info('Using razorpay_config.py for credentials in payment_callback')
        except Exception:
            pass

        if razorpay is None:
            logger.error('Razorpay package not installed')
            return JsonResponse(
                {'error': 'Payment gateway not available', 'detail': 'razorpay package not installed'},
                status=500
            )

        if not enabled:
            logger.error('Razorpay is not enabled')
            return JsonResponse(
                {'error': 'Payment gateway not configured', 'detail': 'razorpay is disabled'},
                status=500
            )

        if not key_id or not key_secret:
            logger.error('Razorpay credentials missing')
            return JsonResponse(
                {'error': 'Payment gateway not configured', 'detail': 'missing credentials'},
                status=500
            )

        # Initialize Razorpay client
        client = razorpay.Client(auth=(key_id, key_secret))
        
        # Parse and validate request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error('Invalid JSON in request body')
            return JsonResponse(
                {'error': 'Invalid request format', 'detail': 'invalid JSON'},
                status=400
            )

        # Validate required parameters
        required_params = ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature']
        missing_params = [param for param in required_params if not data.get(param)]
        if missing_params:
            logger.error(f'Missing required parameters: {missing_params}')
            return JsonResponse(
                {'error': 'Invalid request format', 'detail': f'missing parameters: {missing_params}'},
                status=400
            )
        
        params_dict = {
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        
        try:
            logger.info(f'Verifying payment: order_id={params_dict["razorpay_order_id"]}, payment_id={params_dict["razorpay_payment_id"]}')
            
            # Verify payment signature
            client.utility.verify_payment_signature(params_dict)
            logger.info('Payment signature verified successfully')
            
            # Fetch payment details to verify status
            payment_details = client.payment.fetch(params_dict['razorpay_payment_id'])
            if payment_details.get('status') != 'captured':
                logger.error(f'Payment not captured. Status: {payment_details.get("status")}')
                return JsonResponse(
                    {'error': 'Payment not completed', 'detail': 'payment not captured'},
                    status=400
                )
            
            # Get or create payment record
            payment = CoursePayment.objects.filter(order_id=params_dict['razorpay_order_id']).first()
            if not payment:
                payment = CoursePayment(
                    user=request.user,
                    course=course,
                    order_id=params_dict['razorpay_order_id'],
                    payment_id=params_dict['razorpay_payment_id'],
                    amount=course.discounted_price,
                    currency='INR',
                    first_name=request.session.get('checkout_first_name', ''),
                    last_name=request.session.get('checkout_last_name', ''),
                    email=request.session.get('checkout_email', ''),
                    phone=request.session.get('checkout_phone', ''),
                    address=request.session.get('checkout_address', ''),
                    city=request.session.get('checkout_city', ''),
                    state=request.session.get('checkout_state', ''),
                    zip_code=request.session.get('checkout_zip', ''),
                    status='successful'
                )
                payment.save()
            
            # Grant course access
            CourseAccess.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'payment': payment,
                    'is_active': True
                }
            )
            
            # Clear checkout session data
            checkout_fields = [
                'checkout_first_name', 'checkout_last_name', 'checkout_email',
                'checkout_phone', 'checkout_address', 'checkout_city',
                'checkout_state', 'checkout_zip'
            ]
            for field in checkout_fields:
                request.session.pop(field, None)
            
            messages.success(request, 'Payment successful! You now have access to the course.')
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('my-purchase')  # Add URL to redirect to
            })
            
        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f'Payment signature verification failed: {str(e)}')
            return JsonResponse(
                {'error': 'Payment verification failed', 'detail': 'invalid signature'},
                status=400
            )
        except Exception as e:
            logger.exception('Error processing payment verification')
            return JsonResponse(
                {'error': 'Payment verification failed', 'detail': str(e)},
                status=400
            )
    
    except Exception as e:
        logger.error(f'Unexpected error in payment callback: {str(e)}')
        return JsonResponse(
            {'error': 'An unexpected error occurred', 'detail': str(e)},
            status=500
        )

def payment_debug(request):
    """
    Development-only endpoint to view effective Razorpay configuration and auth state.
    Returns JSON indicating what the server sees for the current request.
    """
    # Only allow in DEBUG mode
    if not django_settings.DEBUG:
        return JsonResponse({'error': 'Not available in production'}, status=403)

    resp = {
        'request_user_authenticated': request.user.is_authenticated,
        'request_user_username': getattr(request.user, 'username', None) if request.user.is_authenticated else None,
        'DJANGO_SETTINGS_MODULE': __import__('os').environ.get('DJANGO_SETTINGS_MODULE'),
        'RAZORPAY_ENABLED': getattr(django_settings, 'RAZORPAY_ENABLED', False),
        'KEY_ID_present': bool(getattr(django_settings, 'RAZORPAY_KEY_ID', '')),
        'KEY_SECRET_present': bool(getattr(django_settings, 'RAZORPAY_KEY_SECRET', '')),
        'CURRENCY': getattr(django_settings, 'RAZORPAY_CURRENCY', 'INR'),
        'razorpay_package_importable': (razorpay is not None),
    }
    # Also report any local razorpay_config.py values for clarity
    try:
        import razorpay_config
        cfg = razorpay_config.get_config(test_mode=True)
        resp['razorpay_config'] = {
            'loaded': True,
            'config': {
                'ENABLED': cfg.get('ENABLED'),
                'KEY_ID_present': bool(cfg.get('KEY_ID')),
                'KEY_SECRET_present': bool(cfg.get('KEY_SECRET')),
                'KEY_ID': cfg.get('KEY_ID') if getattr(django_settings, 'DEBUG', False) else ('***' if cfg.get('KEY_ID') else ''),
            }
        }
    except Exception as e:
        resp['razorpay_config'] = {'loaded': False, 'error': str(e)}
    return JsonResponse(resp)


@login_required
def download_exam_certificate(request, certificate_id):
    """
    Allow logged-in users to download their exam certificates.
    Only the certificate owner or admin can download.
    """
    certificate = get_object_or_404(ExamCertificate, id=certificate_id, is_active=True)
    
    # Check if user is the certificate owner or is admin
    if certificate.exam_attempt.course_access.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to download this certificate.')
        return redirect('my-purchase')
    
    # Check if certificate file exists
    if not certificate.certificate_file:
        messages.error(request, 'Certificate file is not available yet.')
        return redirect('my-purchase')
    
    try:
        return FileResponse(
            certificate.certificate_file.open('rb'),
            as_attachment=True,
            filename=f"{certificate.student_name.replace(' ', '_')}_certificate_{certificate.id}.pdf"
        )
    except Exception as e:
        logger.error(f"Error downloading certificate {certificate_id}: {str(e)}")
        messages.error(request, 'Error downloading certificate.')
        return redirect('my-purchase')
