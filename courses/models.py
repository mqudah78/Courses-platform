from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
User = settings.AUTH_USER_MODEL

class Course(models.Model):
    DELIVERY_MODES = (
        ('online','Online'),
        ('live','Live'),
        ('class','In-Class'),
    )

    title = models.CharField(max_length=200)
    description =models.TextField()
    instructor = models.ForeignKey(
    User,on_delete=models.CASCADE,
    related_name='courses'
    )
    delivery_mode = models.CharField(max_length=10,choices=DELIVERY_MODES)

    price = models.DecimalField(max_digits=8, decimal_places=2,default=0)
    duration_hours =models.PositiveIntegerField(default=20)

    capacity = models.PositiveIntegerField(default=30) 
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def seats_left(self): 
        return self.capacity - self.enrollments.count()

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Session(models.Model):
    SESSION_TYPE_CHOICES = (
        ('LIVE', 'Live (Online)'),
        ('CLASS', 'In-Class'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    title = models.CharField(max_length=200)
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    zoom_link = models.URLField(blank=True, null=True)
    classroom = models.CharField(max_length=100, blank=True, null=True)

    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0)  # <-- new field

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def update_progress(self):
        total_lessons = Lesson.objects.filter(
            module__course=self.course
        ).count()

        if total_lessons == 0:
            self.progress = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                enrollment=self,
                completed=True
            ).count()

            self.progress = (completed_lessons / total_lessons) * 100

        self.save()


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment,on_delete=models.CASCADE)
    lesson =models.ForeignKey(Lesson,on_delete=models.CASCADE)
    completed =models.BooleanField(default=False)
    completed_at =models.DateTimeField(null=True,blank=True)

    class Meta:
        unique_together = ('enrollment','lesson')

        

class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'session')


class CourseRegistration(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    preferred_date = models.CharField(max_length=100, blank=True, null=True)

    experience_level = models.CharField(max_length=50, choices=[
        ('Beginner', 'Beginner'),
        ('Some Experience', 'Some Experience'),
    ])

    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)