from django import forms
from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.utils.html import format_html
import csv
import io
from collections import defaultdict
from .models import (
    CourseFeature, CourseOverview, CourseSkill, CourseTool, CourseBrochure,
    CoursePayment, CourseAccess, CourseExam, ExamQuestion, ExamAttempt, ExamAnswer, ExamViolation
)
from .models_brochure import BrochureDownload
from .admin_brochure import BrochureDownloadAdmin
from django.urls import path, reverse
from django.shortcuts import render
from django.forms import formset_factory
from django.shortcuts import get_object_or_404
# Register CourseFeature for admin control
@admin.register(CourseFeature)
class CourseFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    ordering = ('course', 'order')

@admin.register(CourseOverview)
class CourseOverviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('course', 'order')

@admin.register(CourseSkill)
class CourseSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('name',)
    list_editable = ('order', 'is_active')
    ordering = ('course', 'order')

@admin.register(CourseTool)
class CourseToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('name',)
    list_editable = ('order', 'is_active')
    ordering = ('course', 'order')

@admin.register(CourseBrochure)
class CourseBrochureAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'is_active', 'updated_at')
    list_filter = ('course', 'is_active')
    search_fields = ('course__name', 'title')
    list_editable = ('is_active',)
    ordering = ('course',)
from django.contrib import admin
from .models import (
    Section, Content, HeroBanner, AboutPage, AboutSection, 
    FeatureCard, HomeAboutSection, CourseCategory, CourseBrowser,
    LearningBanner, WhyChoose, WhyChooseItem, CertificateSection,
    FAQQuestion, TestimonialStrip, Course, CourseInstructor
    , CourseLocalInstructor
)
from .models import CourseScheduleDay, CourseScheduleItem

class ContentInline(admin.TabularInline):
    model = Content
    extra = 1
    fields = ('title', 'content', 'image', 'order', 'is_active')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentInline]
    list_editable = ('order', 'is_active')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'image', 'order', 'is_active')}),
        ('Styling', {'fields': ('background_color', 'text_color', 'custom_css'), 'classes': ('collapse',)}),
    )
    # show font size in styling section
    def get_fieldsets(self, request, obj=None):
        fs = list(self.fieldsets)
        # insert text_font_size into Styling if present
        fs[1][1]['fields'] = tuple(list(fs[1][1]['fields']) + ['text_font_size'])
        return tuple(fs)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)
        
from django.contrib import admin
from .models import *

@admin.register(CoursePurchaseCard)
class CoursePurchaseCardAdmin(admin.ModelAdmin):
    """Admin interface for CoursePurchaseCard model."""
    list_display = ['course', 'title', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['course__name', 'title']
    raw_id_fields = ['course']
    fieldsets = (
        ('Course', {
            'fields': ('course',)
        }),
        ('Card Content', {
            'fields': (
                'card_image',
                'title',
                'description',
                'button_text',
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['title', 'highlight_text']
    list_editable = ('is_active',)
    fieldsets = (
        (None, {'fields': ('title', 'highlight_text', 'image', 'button_text', 'button_url', 'is_active')}),
        ('Styling', {'fields': ('overlay_color', 'text_color', 'button_background', 'button_text_color'), 'classes': ('collapse',)}),
    )
    def get_fieldsets(self, request, obj=None):
        fs = list(self.fieldsets)
        fs[1][1]['fields'] = tuple(list(fs[1][1]['fields']) + ['text_font_size', 'button_font_size'])
        return tuple(fs)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)
        
@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active',)
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'main_image', 'is_active')}),
        ('Styling', {'fields': ('background_color', 'text_color'), 'classes': ('collapse',)}),
    )
    def get_fieldsets(self, request, obj=None):
        fs = list(self.fieldsets)
        fs[1][1]['fields'] = tuple(list(fs[1][1]['fields']) + ['text_font_size'])
        return tuple(fs)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)
        
@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'order', 'is_active', 'updated_at')
    list_filter = ('section_type', 'is_active')
    search_fields = ('title', 'content')
    list_editable = ('order', 'is_active')
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)
        
    def save_formset(self, request, form, formset, change):
        """Override save_formset to ensure related content changes are saved immediately."""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()


@admin.register(LearningBanner)
class LearningBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'highlight', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'highlight', 'subtitle')
    list_editable = ('is_active',)
    fieldsets = (
        (None, {'fields': ('title', 'highlight', 'subtitle', 'image', 'button_text', 'button_url', 'is_active')}),
    )

    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)



class WhyChooseItemInline(admin.TabularInline):
    model = WhyChooseItem
    extra = 1
    fields = ('text', 'image', 'order', 'is_active', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-height:60px;" />'
        return ''
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


@admin.register(WhyChoose)
class WhyChooseAdmin(admin.ModelAdmin):
    list_display = ('section_title', 'section_subtitle', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('section_title', 'section_subtitle')
    inlines = [WhyChooseItemInline]
    fieldsets = (
        (None, {'fields': ('section_title', 'section_subtitle', 'is_active')}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


# WhyChooseItem is intentionally not registered as a top-level ModelAdmin so it is
# managed inline under WhyChooseAdmin (WhyChooseItemInline above). This keeps
# the admin index simpler and avoids duplicated entry points for editing items.

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'is_active', 'updated_at')
    list_filter = ('section', 'is_active')
    search_fields = ('title', 'content')
    list_editable = ('order', 'is_active')
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)
        
@admin.register(FeatureCard)
class FeatureCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'card_title', 'order', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('card_title', 'card_description')
    list_editable = ('order', 'is_active')
    fieldsets = (
        (None, {'fields': ('card_number', 'card_title', 'card_description', 'card_image', 'order', 'is_active')}),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)

@admin.register(HomeAboutSection)
class HomeAboutSectionAdmin(admin.ModelAdmin):
    list_display = ('section_label', 'main_heading', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('section_label', 'main_heading', 'description')
    fieldsets = (
        (None, {'fields': ('section_label', 'main_heading', 'description', 'image', 'is_active')}),
        ('Button Options', {'fields': ('button_text', 'button_url')}),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)


@admin.register(CertificateSection)
class CertificateSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active',)
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'image', 'is_active')}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(FAQQuestion)
class FAQQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active', 'order')
    ordering = ('order',)
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active', 'order')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)

@admin.register(CourseBrowser)
class CourseBrowserAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name',)
    list_editable = ('is_active', 'order')
    ordering = ('order',)
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'category', 'is_active', 'order')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are saved immediately."""
        super().save_model(request, obj, form, change)

@admin.register(TestimonialStrip)
class TestimonialStripAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('order', 'is_active')
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'description', 'image', 'order', 'is_active')}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class CourseInstructorInline(admin.TabularInline):
    model = CourseInstructor
    extra = 1
    fields = ('instructor', 'order', 'is_primary')

class CourseLocalInstructorInline(admin.TabularInline):
    model = CourseLocalInstructor
    extra = 1
    fields = ('name', 'image', 'order', 'is_primary', 'is_active')
    readonly_fields = ()


class CourseScheduleDayInline(admin.TabularInline):
    """Allow quick adding of schedule days directly on the Course admin."""
    model = CourseScheduleDay
    extra = 1
    fields = ('title', 'order', 'is_active', 'items_preview')
    readonly_fields = ('items_preview',)
    show_change_link = True

    def items_preview(self, obj):
        """Render a compact preview of items for this day: thumbnail(s) or video links."""
        if not obj.pk:
            return ''
        items = obj.items.all()[:5]
        parts = []
        for it in items:
            if it.thumbnail:
                parts.append(format_html('<a href="{}" target="_blank"><img src="{}" style="height:40px;margin-right:6px;" /></a>', it.thumbnail.url, it.thumbnail.url))
            elif it.video_file:
                parts.append(format_html('<a href="{}" target="_blank">{}</a>', it.video_file.url, it.title))
            elif it.video_url:
                parts.append(format_html('<a href="{}" target="_blank">{}</a>', it.video_url, it.title))
        if obj.items.count() > 5:
            parts.append(format_html('<span style="margin-left:6px;">(+{} more)</span>', obj.items.count() - 5))
        return format_html(''.join(parts))
    items_preview.allow_tags = True
    items_preview.short_description = 'Items'

@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'course__name', 'order_id', 'payment_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(CourseAccess)
class CourseAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'course__name')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'original_price', 'discounted_price', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active')
    # detailed_description removed from model; keep searchable fields minimal
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    # Keep both the global CourseInstructor inline (select existing instructors)
    # and the CourseLocalInstructor inline (manual per-course instructor entries).
    # Also allow quick creation of schedule days inline. Detailed schedule items
    # should be edited from their own admin so they can be ordered per-day.
    inlines = [CourseInstructorInline, CourseLocalInstructorInline, CourseScheduleDayInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Course Details', {
            'fields': ('category', 'original_price', 'discounted_price', 'buy_url')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Inject a bulk-upload URL into the Course change form when editing a course.
        The URL opens the CourseScheduleDayAdmin bulk-upload view with the course preselected.
        """
        if extra_context is None:
            extra_context = {}
        # Inject the 90-row bulk upload URL and the multi-video-per-day upload URL
        if object_id:
            try:
                bulk90 = reverse('admin:core_course_bulk_day_upload_90', args=(object_id,))
                extra_context['bulk_day_90_url'] = bulk90
            except Exception:
                pass
            try:
                bulk_multi = reverse('admin:core_course_bulk_multi_day_upload', args=(object_id,))
                extra_context['bulk_multi_day_url'] = bulk_multi
            except Exception:
                pass
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    change_list_template = 'admin/core/course/change_list.html'

    def changelist_view(self, request, extra_context=None):
        """Inject a global uploader link into the Course changelist page."""
        if extra_context is None:
            extra_context = {}
        try:
            extra_context['bulk_multi_global_url'] = reverse('admin:core_course_bulk_multi_day_global')
        except Exception:
            pass
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:object_id>/bulk-day-upload-90/', self.admin_site.admin_view(self.bulk_day_upload_90_view), name='core_course_bulk_day_upload_90'),
            path('<int:object_id>/bulk-multi-day-upload/', self.admin_site.admin_view(self.bulk_multi_day_upload_view), name='core_course_bulk_multi_day_upload'),
            path('bulk-multi-day/', self.admin_site.admin_view(self.bulk_multi_day_global_view), name='core_course_bulk_multi_day_global'),
        ]
        return custom + urls

    def bulk_day_upload_90_view(self, request, object_id):
        """Per-course view: display 90 rows where each row creates a Day + one Item.

        Each row fields: day_title, item_title, thumbnail, video_file, order, is_active, DELETE.
        Only non-empty rows will be created.
        """
        course = get_object_or_404(Course, pk=object_id)

        class DayItemForm(forms.Form):
            day_title = forms.CharField(required=False, label='Day title')
            item_title = forms.CharField(required=False, label='Video title')
            thumbnail = forms.ImageField(required=False)
            video_file = forms.FileField(required=False)
            order = forms.IntegerField(required=False, initial=0)
            is_active = forms.BooleanField(required=False, initial=True)
            DELETE = forms.BooleanField(required=False)

        DayItemFormSet = formset_factory(DayItemForm, extra=90)

        if request.method == 'POST':
            formset = DayItemFormSet(request.POST, request.FILES)
            if formset.is_valid():
                created = 0
                with transaction.atomic():
                    # start orders after existing days
                    max_order = CourseScheduleDay.objects.filter(course=course).aggregate(Max('order'))['order__max'] or 0
                    for f in formset:
                        cd = f.cleaned_data
                        if not cd:
                            continue
                        if cd.get('DELETE'):
                            continue
                        # if row empty, skip
                        if not (cd.get('day_title') or cd.get('video_file') or cd.get('item_title')):
                            continue
                        max_order += 1
                        day_title = cd.get('day_title') or f'Day {max_order:02d}'
                        day = CourseScheduleDay.objects.create(course=course, title=day_title, order=max_order)
                        item = CourseScheduleItem(day=day, title=cd.get('item_title') or (getattr(cd.get('video_file'), 'name', '') or '').rsplit('.', 1)[0], order=cd.get('order') or 0, is_active=cd.get('is_active', True))
                        if cd.get('video_file'):
                            item.video_file = cd.get('video_file')
                        if cd.get('thumbnail'):
                            item.thumbnail = cd.get('thumbnail')
                        item.save()
                        created += 1

                self.message_user(request, f'Created {created} days and items for course "{course.name}".', level=messages.SUCCESS)
                return HttpResponseRedirect(reverse('admin:core_course_change', args=(course.pk,)))
        else:
            formset = DayItemFormSet()

        context = dict(self.admin_site.each_context(request), course=course, formset=formset, title='Bulk 90-row day upload')
        return render(request, 'admin/core/course/bulk_day_90.html', context)

    def bulk_multi_day_upload_view(self, request, object_id):
        """Per-course view: allow admins to create multiple Days where each Day
        can have one or more video files. The UI shows multiple rows; each row
        accepts multiple video files (one or more)."""
        course = get_object_or_404(Course, pk=object_id)

        class MultiDayForm(forms.Form):
            day_title = forms.CharField(required=False, label='Day title')
            # Per-row base title applied to each video file in this row.
            base_item_title = forms.CharField(required=False, label='Video title', help_text='Applied to each uploaded file in this row if provided')
            # Optional thumbnail applied to each created item for this row.
            thumbnail = forms.ImageField(required=False, label='Thumbnail')
            # Do not set `multiple` on the widget constructor (some Django versions raise).
            # We'll set `multiple` on the instantiated form's widget attrs after creating the formset.
            files = forms.FileField(required=False, label='Video files')
            order = forms.IntegerField(required=False, initial=0)
            is_active = forms.BooleanField(required=False, initial=True)
            DELETE = forms.BooleanField(required=False)

        MultiDayFormSet = formset_factory(MultiDayForm, extra=10)

        if request.method == 'POST':
            formset = MultiDayFormSet(request.POST, request.FILES)
            if formset.is_valid():
                created_days = 0
                created_items = 0
                with transaction.atomic():
                    max_order = CourseScheduleDay.objects.filter(course=course).aggregate(Max('order'))['order__max'] or 0
                    for f in formset:
                        cd = f.cleaned_data
                        if not cd:
                            continue
                        if cd.get('DELETE'):
                            continue
                        files = request.FILES.getlist(f.prefix + '-files') if f.prefix else []
                        # Django formset prefixes file inputs as <form-prefix>-files when retrieving from FILES
                        if not files:
                            # fallback: sometimes getlist with field name 'files' works
                            files = request.FILES.getlist('files')
                        if not files:
                            # empty row, skip
                            continue
                        max_order += 1
                        day_title = cd.get('day_title') or f'Day {max_order:02d}'
                        day = CourseScheduleDay.objects.create(course=course, title=day_title, order=max_order, is_active=cd.get('is_active', True))
                        created_days += 1
                        for file_obj in files:
                            # Use provided base_item_title or file name
                            item_title = cd.get('base_item_title') or file_obj.name.rsplit('.', 1)[0]
                            item = CourseScheduleItem(day=day, title=item_title, order=cd.get('order') or 0, is_active=cd.get('is_active', True))
                            if cd.get('thumbnail'):
                                item.thumbnail = cd.get('thumbnail')
                            item.video_file = file_obj
                            item.save()
                            created_items += 1

                self.message_user(request, f'Created {created_days} days and {created_items} videos for course "{course.name}".', level=messages.SUCCESS)
                return HttpResponseRedirect(reverse('admin:core_course_change', args=(course.pk,)))
        else:
            formset = MultiDayFormSet()

        # Ensure the file input widgets allow multiple files without passing
        # `multiple` to the widget constructor which can raise a ValueError.
        for f in formset.forms:
            try:
                f.fields['files'].widget.attrs['multiple'] = True
            except Exception:
                pass

        context = dict(self.admin_site.each_context(request), course=course, formset=formset, title='Bulk multi-video day upload')
        return render(request, 'admin/core/course/bulk_multi_day.html', context)

    def bulk_multi_day_global_view(self, request):
        """Global admin view: first select a Course, then show its existing
        days and allow adding upcoming days where each day may contain
        one-or-more video files.
        """
        from django import forms as djforms
        from .models import Course as CourseModel

        class CourseSelectForm(djforms.Form):
            course = djforms.ModelChoiceField(queryset=Course.objects.all(), required=True, label='Select course')

        # Reuse the MultiDayForm logic used in per-course view
        class MultiDayForm(djforms.Form):
            day_title = djforms.CharField(required=False, label='Day title')
            base_item_title = djforms.CharField(required=False, label='Video title', help_text='Applied to each uploaded file in this row if provided')
            thumbnail = djforms.ImageField(required=False, label='Thumbnail')
            files = djforms.FileField(required=False, label='Video files')
            order = djforms.IntegerField(required=False, initial=0)
            is_active = djforms.BooleanField(required=False, initial=True)
            DELETE = djforms.BooleanField(required=False)

        MultiDayFormSet = formset_factory(MultiDayForm, extra=10)

        selected_course = None
        if request.method == 'POST':
            # course should be passed as POST field
            select_form = CourseSelectForm(request.POST)
            formset = MultiDayFormSet(request.POST, request.FILES)
            if select_form.is_valid() and formset.is_valid():
                selected_course = select_form.cleaned_data['course']
                created_days = 0
                created_items = 0
                with transaction.atomic():
                    max_order = CourseScheduleDay.objects.filter(course=selected_course).aggregate(Max('order'))['order__max'] or 0
                    for f in formset:
                        cd = f.cleaned_data
                        if not cd:
                            continue
                        if cd.get('DELETE'):
                            continue
                        files = request.FILES.getlist(f.prefix + '-files') if f.prefix else []
                        if not files:
                            files = request.FILES.getlist('files')
                        if not files:
                            continue
                        max_order += 1
                        day_title = cd.get('day_title') or f'Day {max_order:02d}'
                        day = CourseScheduleDay.objects.create(course=selected_course, title=day_title, order=max_order, is_active=cd.get('is_active', True))
                        created_days += 1
                        for file_obj in files:
                            item_title = cd.get('base_item_title') or file_obj.name.rsplit('.', 1)[0]
                            item = CourseScheduleItem(day=day, title=item_title, order=cd.get('order') or 0, is_active=cd.get('is_active', True))
                            if cd.get('thumbnail'):
                                item.thumbnail = cd.get('thumbnail')
                            item.video_file = file_obj
                            item.save()
                            created_items += 1

                self.message_user(request, f'Created {created_days} days and {created_items} videos for course "{selected_course.name}".', level=messages.SUCCESS)
                return HttpResponseRedirect(reverse('admin:core_course_bulk_multi_day_global') + f'?course={selected_course.pk}')
        else:
            # GET: show selection form and, if course specified, show existing days + formset
            pre_course_id = request.GET.get('course')
            if pre_course_id:
                try:
                    selected_course = Course.objects.get(pk=int(pre_course_id))
                    select_form = CourseSelectForm(initial={'course': selected_course})
                except Exception:
                    select_form = CourseSelectForm()
            else:
                select_form = CourseSelectForm()
            formset = MultiDayFormSet()

        # Set multiple attr on file inputs after formset instantiation to avoid
        # widget constructor errors on some Django versions.
        for f in formset.forms:
            try:
                f.fields['files'].widget.attrs['multiple'] = True
            except Exception:
                pass

        existing_days = []
        if selected_course:
            existing_days = CourseScheduleDay.objects.filter(course=selected_course).prefetch_related('items').order_by('order')

        context = dict(self.admin_site.each_context(request), select_form=select_form, course=selected_course, existing_days=existing_days, formset=formset, title='Bulk multi-video upload (select course)')
        return render(request, 'admin/core/course/bulk_multi_day_global.html', context)


# Schedule admin
class CourseScheduleItemInline(admin.TabularInline):
    model = CourseScheduleItem
    extra = 1
    # Keep the inline minimal for admins: title, thumbnail image, uploaded file, ordering and active flag
    fields = ('title', 'thumbnail', 'video_file', 'order', 'is_active')


@admin.register(CourseScheduleDay)
class CourseScheduleDayAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_active', 'updated_at')
    list_filter = ('course', 'is_active')
    search_fields = ('title', 'course__name')
    inlines = [CourseScheduleItemInline]
    list_editable = ('order', 'is_active')
    ordering = ('course', 'order')

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Inject bulk-upload URL into the CourseScheduleDay change form so admins
        can open the bulk-upload form preselected for this day.course.
        """
        if extra_context is None:
            extra_context = {}
        # Do not provide the older bulk upload URL here; keep default context.
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    # Legacy bulk-upload view removed to keep only the 90-row per-course upload.


@admin.register(CourseScheduleItem)
class CourseScheduleItemAdmin(admin.ModelAdmin):
    # Minimal list display without thumbnail/duration to match admin preference
    list_display = ('title', 'day', 'order', 'is_active')
    list_filter = ('day__course', 'is_active')
    # Remove description from searchable fields since it's no longer editable in admin
    search_fields = ('title', 'day__title')
    list_editable = ('order', 'is_active')
    ordering = ('day', 'order')
    fieldsets = (
        (None, {'fields': ('day', 'title', 'thumbnail')}),
        ('Video', {'fields': ('video_file',)}),
        ('Options', {'fields': ('order', 'is_active')}),
    )


# ============ EXAM ADMIN ============

class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 0
    fields = ('order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'is_active')
    ordering = ['order']


@admin.register(CourseExam)
class CourseExamAdmin(admin.ModelAdmin):
    list_display = ('course', 'duration_minutes', 'passing_score', 'max_attempts', 'question_count', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('course__name',)
    list_editable = ('duration_minutes', 'passing_score', 'max_attempts', 'is_active')
    inlines = [ExamQuestionInline]
    fieldsets = (
        (None, {'fields': ('course', 'title', 'description')}),
        ('Exam Settings', {
            'fields': ('duration_minutes', 'passing_score', 'max_attempts', 'is_active'),
            'description': 'Configure exam duration (minutes), passing score (%), max attempts, and active status.'
        }),
    )
    readonly_fields = ('updated_at',)

    def question_count(self, obj):
        """Display the number of active questions in the exam."""
        count = obj.questions.filter(is_active=True).count()
        return format_html('<strong>{}</strong> questions', count)
    question_count.short_description = 'Questions'

    def get_urls(self):
        """Add custom bulk Q&A upload endpoint."""
        urls = super().get_urls()
        custom = [
            path('<int:object_id>/bulk-questions-upload/', self.admin_site.admin_view(self.bulk_questions_upload_view), name='core_courseexam_bulk_questions_upload'),
        ]
        return custom + urls

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Inject bulk Q&A upload URL into the exam change form."""
        if extra_context is None:
            extra_context = {}
        if object_id:
            try:
                bulk_url = reverse('admin:core_courseexam_bulk_questions_upload', args=(object_id,))
                extra_context['bulk_questions_upload_url'] = bulk_url
            except Exception:
                pass
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def bulk_questions_upload_view(self, request, object_id):
        """Bulk Q&A upload view: accepts CSV with columns:
        order, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, is_active
        """
        exam = get_object_or_404(CourseExam, pk=object_id)

        if request.method == 'POST' and 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            try:
                file_content = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(file_content))

                if not reader.fieldnames:
                    self.message_user(request, 'CSV file is empty.', level=messages.ERROR)
                    return HttpResponseRedirect(reverse('admin:core_courseexam_change', args=(exam.pk,)))

                expected_fields = {'order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'}
                if not expected_fields.issubset(set(reader.fieldnames or [])):
                    self.message_user(
                        request,
                        f'CSV must have columns: order, question_text, option_a, option_b, option_c, option_d, correct_answer, and optionally explanation, is_active.',
                        level=messages.ERROR
                    )
                    return HttpResponseRedirect(reverse('admin:core_courseexam_change', args=(exam.pk,)))

                created = 0
                errors = []
                with transaction.atomic():
                    for row_idx, row in enumerate(reader, start=2):  # start at 2 because header is row 1
                        try:
                            if not row.get('question_text', '').strip():
                                continue

                            order_str = (row.get('order', '') or '0').strip()
                            try:
                                order = int(order_str) if order_str else created
                            except ValueError:
                                order = created

                            correct = (row.get('correct_answer', '') or 'A').strip().upper()
                            if correct not in ['A', 'B', 'C', 'D']:
                                errors.append(f'Row {row_idx}: correct_answer must be A, B, C, or D')
                                continue

                            is_active_str = (row.get('is_active', 'true') or 'true').strip().lower()
                            is_active = is_active_str in ['true', '1', 'yes']

                            ExamQuestion.objects.create(
                                exam=exam,
                                order=order,
                                question_text=row.get('question_text', '').strip(),
                                option_a=row.get('option_a', '').strip(),
                                option_b=row.get('option_b', '').strip(),
                                option_c=row.get('option_c', '').strip(),
                                option_d=row.get('option_d', '').strip(),
                                correct_answer=correct,
                                explanation=row.get('explanation', '').strip() or '',
                                is_active=is_active
                            )
                            created += 1
                        except Exception as e:
                            errors.append(f'Row {row_idx}: {str(e)}')

                msg = f'Uploaded {created} questions successfully.'
                if errors:
                    msg += f' ({len(errors)} errors: ' + '; '.join(errors[:5]) + (f'; and {len(errors) - 5} more...' if len(errors) > 5 else '') + ')'
                    self.message_user(request, msg, level=messages.WARNING if created > 0 else messages.ERROR)
                else:
                    self.message_user(request, msg, level=messages.SUCCESS)

                return HttpResponseRedirect(reverse('admin:core_courseexam_change', args=(exam.pk,)))
            except Exception as e:
                self.message_user(request, f'Error processing CSV: {str(e)}', level=messages.ERROR)
                return HttpResponseRedirect(reverse('admin:core_courseexam_change', args=(exam.pk,)))

        context = dict(
            self.admin_site.each_context(request),
            exam=exam,
            title=f'Bulk Q&A Upload - {exam.course.name}'
        )
        return render(request, 'admin/core/courseexam/bulk_questions_upload.html', context)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'exam', 'question_text_short', 'correct_answer', 'is_active')
    list_filter = ('exam__course', 'exam', 'is_active')
    search_fields = ('exam__course__name', 'question_text')
    list_editable = ('is_active',)
    fieldsets = (
        ('Question', {
            'fields': ('exam', 'order', 'question_text'),
            'description': 'Set the question order and text.'
        }),
        ('Answer Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'),
            'description': 'Provide all four answer options (A, B, C, D) and select the correct one.',
            'classes': ('wide',)
        }),
        ('Additional Info', {
            'fields': ('explanation', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    def question_text_short(self, obj):
        """Display shortened question text in list view."""
        text = obj.question_text[:60]
        return text + '...' if len(obj.question_text) > 60 else text
    question_text_short.short_description = 'Question'


class ExamAnswerInline(admin.TabularInline):
    model = ExamAnswer
    extra = 0
    fields = ('question', 'selected_answer', 'is_correct')
    readonly_fields = ('question', 'selected_answer', 'is_correct')
    can_delete = False


class ExamViolationInline(admin.TabularInline):
    model = ExamViolation
    extra = 0
    readonly_fields = ('violation_type', 'violation_count', 'description', 'recorded_at', 'auto_submitted')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('course_access', 'attempt_number', 'is_submitted', 'score_percentage', 'is_passed', 'has_violations_display', 'submitted_at')
    list_filter = ('is_submitted', 'is_passed', 'has_violations', 'submitted_at')
    search_fields = ('course_access__user__email', 'course_access__course__name')
    readonly_fields = ('started_at', 'submitted_at', 'time_taken_seconds', 'score_percentage', 'correct_answers', 'has_violations', 'violation_count')
    inlines = [ExamAnswerInline, ExamViolationInline]
    fieldsets = (
        (None, {'fields': ('course_access', 'attempt_number')}),
        ('Timing', {'fields': ('started_at', 'submitted_at', 'time_taken_seconds')}),
        ('Results', {'fields': ('is_submitted', 'score_percentage', 'correct_answers', 'total_questions', 'is_passed')}),
        ('Security', {'fields': ('has_violations', 'violation_count')}),
    )

    def has_violations_display(self, obj):
        if obj.has_violations:
            return format_html('<span style="color: red; font-weight: bold;">⚠ Violations</span>')
        return '✓ Clean'
    has_violations_display.short_description = 'Security'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ExamViolation)
class ExamViolationAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'violation_type', 'violation_count', 'auto_submitted', 'recorded_at')
    list_filter = ('violation_type', 'auto_submitted', 'recorded_at')
    search_fields = ('attempt__course_access__user__email', 'attempt__course_access__course__name', 'description')
    readonly_fields = ('attempt', 'violation_type', 'violation_count', 'description', 'recorded_at', 'auto_submitted')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
