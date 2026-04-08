from django import forms
from .models import Module, Lesson, Session

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video_url', 'content', 'order']


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'course', 'title', 'session_type',
            'date', 'start_time', 'end_time',
            'zoom_link', 'classroom', 'is_visible'
        ]
