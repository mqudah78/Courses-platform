from django.contrib import admin
from .models import Course, Module, Lesson, Session, Enrollment, Attendance, LessonProgress, CourseRegistration
# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'delivery_mode', 'is_active')
    list_filter = ('delivery_mode', 'is_active')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    ordering = ('course', 'order')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    ordering = ('module', 'order')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'session_type', 'date', 'is_visible')
    list_filter = ('session_type', 'is_visible', 'date')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')

admin.site.register(Attendance)

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        'student_name',
        'lesson',
        'course_name',
        'completed',
        'completed_at'
    )
    list_filter = ('completed', 'lesson__module__course')
    search_fields = (
        'enrollment__student__username',
        'lesson__title'
    )

    def student_name(self, obj):
        return obj.enrollment.student.get_username()

    def course_name(self, obj):
        return obj.lesson.module.course.title

admin.site.register(CourseRegistration)