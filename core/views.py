from django.shortcuts import render
from courses.models import Course

def home(request):
    # Get all active courses
    courses = Course.objects.filter(is_active=True)
    return render(request, 'home.html', {'courses': courses})

def about(request):
    return render(request, 'about.html')
