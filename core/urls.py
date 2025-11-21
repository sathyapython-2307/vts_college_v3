from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import exam_views

urlpatterns = [
    path('', views.home, name='home'),
    # Backwards-compatible numeric course URL -> redirect to slug URL
    path('course/<int:course_id>/', views.course_detail_by_id, name='course_detail_by_id'),
    path('course/<slug:slug>/checkout/', views.course_checkout, name='course_checkout'),
    path('course/<slug:slug>/create-order/', views.create_order, name='create_order'),
    path('course/<slug:slug>/payment-callback/', views.payment_callback, name='payment_callback'),
    path('course/<slug:slug>/brochure/', views.download_brochure, name='download_brochure'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    # Video play tracking endpoints (DB-driven progress)
    path('course/<int:course_id>/video/<int:item_id>/mark-watched/', views.mark_video_watched, name='mark_video_watched'),
    path('course/<int:course_id>/check-completion/', views.check_course_completion, name='check_course_completion'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('my-purchase/', views.my_purchase, name='my-purchase'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('team/', views.team, name='team'),
    path('testimonials/', views.testimonials, name='testimonials'),
    # Dev-only debug endpoint to inspect Razorpay settings during a browser session
    path('payment-debug/', views.payment_debug, name='payment_debug'),
    
    # Exam system URLs
    path('course/<int:course_id>/exam/check-eligibility/', exam_views.exam_check_eligibility, name='exam_check_eligibility'),
    path('course/<int:course_id>/exam/start/', exam_views.exam_start, name='exam_start'),
    path('exam/<int:attempt_id>/', exam_views.exam_portal, name='exam_portal'),
    path('exam/<int:attempt_id>/get-questions/', exam_views.exam_get_questions, name='exam_get_questions'),
    path('exam/<int:attempt_id>/time-left/', exam_views.exam_time_left, name='exam_time_left'),
    path('exam/<int:attempt_id>/save-answer/', exam_views.exam_save_answer, name='exam_save_answer'),
    path('exam/<int:attempt_id>/record-violation/', exam_views.exam_record_violation, name='exam_record_violation'),
    path('exam/<int:attempt_id>/submit/', exam_views.exam_submit, name='exam_submit'),
    path('exam/<int:attempt_id>/results/', exam_views.exam_results, name='exam_results'),
    path('course/<int:course_id>/exam/remind-later/', exam_views.exam_remind_later, name='exam_remind_later'),
]