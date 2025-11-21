from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class HeroBanner(models.Model):
    title = models.CharField(max_length=200)
    highlight_text = models.CharField(max_length=200)
    image = models.ImageField(upload_to='hero_banners/', null=True, blank=True)
    button_text = models.CharField(max_length=50, default="Enroll Now")
    button_url = models.CharField(max_length=200, default="#")
    # Styling options editable from admin
    overlay_color = models.CharField(max_length=50, blank=True, null=True, help_text='Background or overlay color (hex or rgba), e.g. #000000 or rgba(0,0,0,0.5)')
    text_color = models.CharField(max_length=50, blank=True, null=True, help_text='Text color (hex), e.g. #ffffff')
    button_background = models.CharField(max_length=50, blank=True, null=True, help_text='Button background color (hex)')
    button_text_color = models.CharField(max_length=50, blank=True, null=True, help_text='Button text color (hex)')
    # Font sizing
    text_font_size = models.CharField(max_length=20, blank=True, null=True, help_text='Font size for hero text (e.g. 32px, 2rem)')
    button_font_size = models.CharField(max_length=20, blank=True, null=True, help_text='Font size for hero button (e.g. 16px)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hero Banner"
        verbose_name_plural = "Hero Banner"

    def __str__(self):
        return self.title

class Section(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='section_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    # Styling options for sections
    background_color = models.CharField(max_length=50, blank=True, null=True, help_text='Section background color (hex or rgba)')
    text_color = models.CharField(max_length=50, blank=True, null=True, help_text='Section text color (hex)')
    custom_css = models.TextField(blank=True, null=True, help_text='Additional inline CSS declarations for this section (e.g. "padding:40px 0;")')
    # Font sizing for section text
    text_font_size = models.CharField(max_length=20, blank=True, null=True, help_text='Default font size for section text (e.g. 16px, 1rem)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Content(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='content_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['section', 'order']

    def __str__(self):
        return f"{self.section.title} - {self.title}"

class AboutPage(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    main_image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    # Styling options for about page
    background_color = models.CharField(max_length=50, blank=True, null=True, help_text='Page background color (hex or rgba)')
    text_color = models.CharField(max_length=50, blank=True, null=True, help_text='Page text color (hex)')
    text_font_size = models.CharField(max_length=20, blank=True, null=True, help_text='Default font size for About page text (e.g. 16px)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return self.title

class AboutSection(models.Model):
    SECTION_TYPES = (
        ('about_us', 'About Us'),
        ('who_we_are', 'Who We Are'),
        ('our_vision', 'Our Vision'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='other')
    image = models.ImageField(upload_to='about_section_images/', blank=True, null=True)
    # Optional styling per about-section
    background_color = models.CharField(max_length=50, blank=True, null=True, help_text='Background color for this about section')
    text_color = models.CharField(max_length=50, blank=True, null=True, help_text='Text color for this about section')
    # Font sizing for about sections
    text_font_size = models.CharField(max_length=20, blank=True, null=True, help_text='Font size for this about section (e.g. 16px)')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "About Section"
        verbose_name_plural = "About Sections"

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title}"

class Course(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the course name", blank=True)
    description = models.TextField(blank=True)
    # NOTE: detailed_description, image and duration were removed per admin change request.
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price before discount")
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Discounted/actual price")
    # Make buy_url default to '#' so new courses without a URL still render
    # a usable (no-op) Buy button. Keep blank=True and null=True to allow
    # admins to explicitly clear or set the field.
    buy_url = models.URLField(max_length=500, null=True, blank=True, default="#", help_text="URL for the Buy Now button")
    category = models.ForeignKey('CourseCategory', on_delete=models.SET_NULL, null=True, blank=True)
    instructors = models.ManyToManyField('Instructor', through='CourseInstructor', related_name='courses')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CourseLocalInstructor(models.Model):
    """Local per-course instructor entries: manual name + image uploads.

    These allow admins to add instructor names and images directly on a Course
    (with "+ Add Another" behaviour via Django inlines) without replacing
    the existing global Instructor/CourseInstructor models.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='local_instructors')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='course_instructor_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Course Local Instructor"
        verbose_name_plural = "Course Local Instructors"

    def __str__(self):
        return f"{self.course.name} - {self.name}"

class Instructor(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    image = models.ImageField(upload_to='instructor_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"

    def __str__(self):
        return self.name

class CourseFeature(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='features')
    icon = models.CharField(max_length=100, help_text='FontAwesome icon class or image URL')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Order of feature display')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.course.name})"

class CourseOverview(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='overviews')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_overview_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Course Overview'
        verbose_name_plural = 'Course Overviews'

    def __str__(self):
        return f"{self.title} ({self.course.name})"

class CourseSkill(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Course Skill'
        verbose_name_plural = 'Course Skills'

    def __str__(self):
        return f"{self.name} ({self.course.name})"

class CourseTool(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='tools')
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='course_tool_icons/', help_text='Tool icon image', null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Course Tool'
        verbose_name_plural = 'Course Tools'

    def __str__(self):
        return f"{self.name} ({self.course.name})"
class Testimonial(models.Model):
    student_name = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonial_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return self.student_name


class CertificateSection(models.Model):
    """Model to control the certificate block on the home page."""
    title = models.CharField(max_length=200, default='VTS Certificate')
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='certificate_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Certificate Section'
        verbose_name_plural = 'Certificate Sections'

    def __str__(self):
        return self.title

class FeatureCard(models.Model):
    card_number = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Card number (e.g. 01, 02)")
    card_title = models.CharField(max_length=100, help_text="Title of the feature card")
    card_description = models.TextField(help_text="Description text for the feature card")
    card_image = models.ImageField(upload_to='feature_cards/', help_text="Icon image for the feature card")
    order = models.IntegerField(default=0, help_text="Order in which cards appear (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Feature Card"
        verbose_name_plural = "Feature Cards"

    def __str__(self):
        return f"{self.card_number:02d} - {self.card_title}"
        
class HomeAboutSection(models.Model):
    section_label = models.CharField(max_length=100, help_text="Section label (e.g. 'About Our Platform')")
    main_heading = models.CharField(max_length=200, help_text="Main heading text")
    description = models.TextField(help_text="Description text for the about section")
    image = models.ImageField(upload_to='home_about_images/', help_text="Image for the about section")
    button_text = models.CharField(max_length=50, default="Browse All Courses", help_text="Text for the call-to-action button")
    button_url = models.CharField(max_length=200, default="#", help_text="URL for the call-to-action button")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Home About Section"
        verbose_name_plural = "Home About Section"

    def __str__(self):
        return self.main_heading
        
class CourseCategory(models.Model):
    """Model for course categories in the course browser section."""
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ['order']
        
    def __str__(self):
        return self.name

class CourseBrowser(models.Model):
    """Model for courses in the course browser section."""
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='course_browser_images/')
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.name


class LearningBanner(models.Model):
    """Model for the large learning CTA/banner on the home page (below courses)."""
    title = models.CharField(max_length=200, help_text='Main title, may include HTML tags if needed')
    highlight = models.CharField(max_length=200, blank=True, null=True, help_text='Highlighted text within the title')
    subtitle = models.CharField(max_length=300, blank=True, null=True, help_text='Secondary text under the title')
    image = models.ImageField(upload_to='learning_banner/', blank=True, null=True)
    button_text = models.CharField(max_length=50, default='Sign up for Free')
    button_url = models.CharField(max_length=200, default='#')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Learning Banner'
        verbose_name_plural = 'Learning Banners'

    def __str__(self):
        return self.title


class WhyChoose(models.Model):
    """Container model for the 'Why Choose Us' section."""
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_subtitle = models.CharField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Why Choose Section'
        verbose_name_plural = 'Why Choose Sections'

    def __str__(self):
        return self.section_title or 'Why Choose Section'


class WhyChooseItem(models.Model):
    """Individual items/cards for the WhyChoose section."""
    section = models.ForeignKey(WhyChoose, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=150)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='why_choose/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Why Choose Item'
        verbose_name_plural = 'Why Choose Items'

    def __str__(self):
        return self.title


class FAQQuestion(models.Model):
    """Frequently asked question for the FAQ accordion."""
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ Question'
        verbose_name_plural = 'FAQ Questions'

    def __str__(self):
        return self.question

class TestimonialStrip(models.Model):
    title = models.CharField(max_length=200, help_text="Title for the testimonials strip")
    subtitle = models.TextField(blank=True, null=True, help_text="Subtitle or description for the testimonials strip")
    description = models.TextField(blank=True, null=True, help_text="Detailed description for the testimonials strip")
    image = models.ImageField(upload_to='testimonial_strip_images/', blank=True, null=True, help_text="Image for the testimonials strip")
    order = models.IntegerField(default=0, help_text="Order in which testimonial strips appear (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Testimonial Strip"
        verbose_name_plural = "Testimonial Strips"

    def __str__(self):
        return self.title

class CourseBrochure(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='brochures')
    title = models.CharField(max_length=200, default='Course Curriculum')
    brochure_file = models.FileField(upload_to='course_brochures/', help_text='PDF file for the course brochure')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course Brochure'
        verbose_name_plural = 'Course Brochures'

    def __str__(self):
        return f"{self.course.name} - Brochure"


class CourseScheduleDay(models.Model):
    """Represents a day/section in a course schedule (e.g. Day 01)."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedule_days')
    title = models.CharField(max_length=200, help_text='Label for this day/section (e.g. "Day 01")')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course', 'order']
        verbose_name = 'Course Schedule Day'
        verbose_name_plural = 'Course Schedule Days'

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class CourseScheduleItem(models.Model):
    """Individual lesson/item under a CourseScheduleDay."""
    day = models.ForeignKey(CourseScheduleDay, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True, help_text='Optional icon class (e.g. fa fa-video) or text')
    # Video-specific fields
    video_url = models.URLField(blank=True, null=True, help_text='External video URL (YouTube/Vimeo)')
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True, help_text='Optional uploaded video file')
    thumbnail = models.ImageField(upload_to='course_video_thumbs/', blank=True, null=True, help_text='Thumbnail image for the video')
    duration = models.CharField(max_length=50, blank=True, null=True, help_text='Video duration (e.g. 12:34)')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day', 'order']
        verbose_name = 'Course Schedule Item'
        verbose_name_plural = 'Course Schedule Items'

    def __str__(self):
        return f"{self.day.course.name} - {self.day.title} - {self.title}"


class VideoPlay(models.Model):
    """Records each time a user plays a specific course video item.

    A single row per (user, course_item) is stored. The existence of a
    VideoPlay row indicates the user has played that specific item at least once.
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='video_plays')
    course_item = models.ForeignKey(CourseScheduleItem, on_delete=models.CASCADE, related_name='plays')
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course_item')
        verbose_name = 'Video Play'
        verbose_name_plural = 'Video Plays'

    def __str__(self):
        return f"{self.user} - {self.course_item} @ {self.played_at.isoformat()}"


class CourseInstructor(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, help_text="Order in which instructors appear for this course")
    is_primary = models.BooleanField(default=False, help_text="Whether this instructor is the primary instructor for the course")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'instructor']
        verbose_name = "Course Instructor"
        verbose_name_plural = "Course Instructors"

    def __str__(self):
        return f"{self.course.name} - {self.instructor.name}"

class CoursePayment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    ], default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Payment"
        verbose_name_plural = "Course Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.course.name} - {self.status}"

class CourseAccess(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    payment = models.ForeignKey(CoursePayment, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Access"
        verbose_name_plural = "Course Accesses"
        unique_together = ['user', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.name}"
    
    @property
    def progress(self):
        """Get or create progress record for this access."""
        from django.utils import timezone
        prog, created = CourseProgress.objects.get_or_create(
            course_access=self,
            defaults={
                'progress_percentage': 0.0,
                'completed_lessons': [],
                'last_accessed': timezone.now()
            }
        )
        return prog

class CourseProgress(models.Model):
    course_access = models.OneToOneField(CourseAccess, on_delete=models.CASCADE, related_name='_progress')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    completed_lessons = models.JSONField(default=list)
    # New flag: user has played every video in the course at least once
    ready_for_exam = models.BooleanField(default=False, help_text='Set when user has played all course videos at least once')
    ready_for_exam_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Course Progress"
        verbose_name_plural = "Course Progress"

    def __str__(self):
        return f"{self.course_access} - {self.progress_percentage}%"
    
    def update_progress(self, completed_lesson_id=None):
        """Update progress when a lesson is completed."""
        if completed_lesson_id and completed_lesson_id not in self.completed_lessons:
            self.completed_lessons.append(completed_lesson_id)
            
        # Calculate total lessons
        total_lessons = CourseScheduleItem.objects.filter(
            day__course=self.course_access.course,
            is_active=True
        ).count()
        
        if total_lessons > 0:
            self.progress_percentage = (len(self.completed_lessons) / total_lessons) * 100
            
            # Check if course is completed
            if self.progress_percentage >= 100 and not self.is_completed:
                from django.utils import timezone
                self.is_completed = True
                self.completion_date = timezone.now()
                self.generate_certificate()
        
        self.save()

    def generate_certificate(self):
        """Generate a certificate upon course completion."""
        if not self.is_completed:
            return
        
        # Generate unique certificate number
        import uuid
        certificate_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        
        # Create certificate if it doesn't exist
        if not hasattr(self, 'certificate'):
            Certificate.objects.create(
                course_progress=self,
                certificate_type='achievement',
                certificate_number=certificate_number
            )

class Certificate(models.Model):
    CERTIFICATE_TYPES = (
        ('achievement', 'Certificate of Achievement'),
        ('participation', 'Statement of Participation'),
    )
    
    course_progress = models.OneToOneField(CourseProgress, on_delete=models.CASCADE, related_name='certificate')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    certificate_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)

    class Meta:
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"{self.certificate_type} - {self.certificate_number}"
    
    def save(self, *args, **kwargs):
        if not self.pdf_file:
            self.generate_pdf()
        super().save(*args, **kwargs)
    
    def generate_pdf(self):
        """Generate PDF certificate."""
        # TODO: Implement PDF generation logic
        pass

class CoursePurchaseCard(models.Model):
    """Model for customizing individual course cards in My Purchase page."""
    course = models.OneToOneField('Course', on_delete=models.CASCADE, related_name='purchase_card')
    card_image = models.ImageField(
        upload_to='course_purchase_cards/',
        help_text='Image shown on the course card'
    )
    title = models.CharField(max_length=200, help_text='Course title shown on the card')
    description = models.TextField(help_text='Short description shown on the card')
    button_text = models.CharField(
        max_length=50, 
        default='Start Learning',
        help_text='Text shown on the button'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Purchase Card"
        verbose_name_plural = "Course Purchase Cards"

    def __str__(self):
        return f"Purchase Card - {self.course.name}"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.course.name
        super().save(*args, **kwargs)


# ============ EXAM SYSTEM MODELS ============

class CourseExam(models.Model):
    """Exam linked to a Course; stores configuration."""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='exam')
    title = models.CharField(max_length=200, default='Course Final Exam')
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=180, help_text='Exam duration in minutes (default 3 hours)')
    passing_score = models.IntegerField(default=80, help_text='Minimum percentage score to pass')
    max_attempts = models.IntegerField(default=3, help_text='Maximum number of attempts allowed')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course Exam'
        verbose_name_plural = 'Course Exams'

    def __str__(self):
        return f'{self.course.name} - {self.title}'


class ExamQuestion(models.Model):
    """Individual MCQ for the exam."""
    exam = models.ForeignKey(CourseExam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(help_text='The question')
    option_a = models.CharField(max_length=500, help_text='Option A')
    option_b = models.CharField(max_length=500, help_text='Option B')
    option_c = models.CharField(max_length=500, help_text='Option C')
    option_d = models.CharField(max_length=500, help_text='Option D')
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField(blank=True, null=True, help_text='Optional explanation shown after exam submission')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Exam Question'
        verbose_name_plural = 'Exam Questions'

    def __str__(self):
        return f'Q{self.order}: {self.question_text[:50]}'


class ExamAttempt(models.Model):
    """Tracks user's exam attempts."""
    course_access = models.ForeignKey(CourseAccess, on_delete=models.CASCADE, related_name='exam_attempts')
    attempt_number = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    is_passed = models.BooleanField(null=True, blank=True, help_text='True if score >= passing_score')
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    correct_answers = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    has_violations = models.BooleanField(default=False, help_text='True if any violations were detected')
    violation_count = models.IntegerField(default=0, help_text='Total number of violations recorded')
    duration_minutes = models.IntegerField(default=150, help_text='Duration in minutes for this attempt (snapshot at creation time)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at']
        unique_together = ['course_access', 'attempt_number']
        verbose_name = 'Exam Attempt'
        verbose_name_plural = 'Exam Attempts'

    def __str__(self):
        return f'{self.course_access.user.email} - {self.course_access.course.name} - Attempt {self.attempt_number}'


class ExamAnswer(models.Model):
    """User's answer to a specific question in an attempt."""
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('', 'Not answered')])
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['attempt', 'question']
        verbose_name = 'Exam Answer'
        verbose_name_plural = 'Exam Answers'

    def __str__(self):
        return f'{self.attempt} - Q{self.question.order}'


class ExamViolation(models.Model):
    """Tracks security violations during exams."""
    VIOLATION_TYPES = [
        ('right_click', 'Right-Click Attempted'),
        ('copy_paste', 'Copy/Paste Attempted'),
        ('dev_tools', 'Developer Tools Opened'),
        ('tab_switch', 'Tab/Window Switch'),
        ('back_button', 'Back Button Navigation'),
        ('fullscreen_exit', 'Fullscreen Exited'),
        ('other', 'Other Violation'),
    ]
    
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='violations')
    violation_type = models.CharField(max_length=20, choices=VIOLATION_TYPES)
    violation_count = models.PositiveIntegerField(default=1, help_text='Number of times this violation occurred')
    description = models.TextField(blank=True, help_text='Additional details about the violation')
    recorded_at = models.DateTimeField(auto_now_add=True)
    auto_submitted = models.BooleanField(default=False, help_text='True if exam was auto-submitted due to this violation')
    
    class Meta:
        ordering = ['-recorded_at']
        unique_together = [('attempt', 'violation_type')]
        verbose_name = 'Exam Violation'
        verbose_name_plural = 'Exam Violations'
    
    def __str__(self):
        return f'{self.attempt} - {self.get_violation_type_display()} ({self.violation_count}x)'