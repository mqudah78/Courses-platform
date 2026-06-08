from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Lesson, Session, Enrollment, LessonProgress, Attendance
from .forms import ModuleForm, LessonForm, SessionForm
from accounts.decorators import instructor_required  
from django.contrib import messages
from django.utils import timezone



def courses_list(request):
    courses = Course.objects.filter(
        is_active=True
    ).select_related('category')

    return render(
        request,
        'courses/courses_list.html',
        {
            'courses': courses,
        }
    )


def course_detail(request, slug):
    """
    Retrieves a single course based on its unique slug 
    and renders its detailed page.
    """
    # 1. Fetch the course matching the slug from the URL, or return a 404 page if it doesn't exist
    course = get_object_or_404(Course, slug=slug)
    
    # 2. Pass that course object into your detail template
    context = {
        'course': course
    }
    
    # 3. Render the page
    return render(request, 'courses/course_detail.html', context)

@login_required
@instructor_required
def course_create(request):
    if request.method == 'POST':
        Course.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            delivery_mode=request.POST['delivery_mode'],
            instructor=request.user
        )
        return redirect('course_list')

    return render(request, 'courses/course_create.html')


from django.shortcuts import render, get_object_or_404
from courses.models import Course, Enrollment

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course

    # Check enrollment
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()

    # If not enrolled → kick back to course page
    if not enrollment:
        return redirect('course_detail', course.id)

    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress
    })


@login_required
@instructor_required
def add_module(request,course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != request.user:
        return redirect('course_detail',course_id=course.id)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = ModuleForm()
    
    return render(request, 'courses/add_module.html', {
        'form': form,
        'course': course
    })

@login_required
@instructor_required
def add_lesson(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    # Ownership check
    if module.course.instructor != request.user:
        return redirect('course_detail', course_id=module.course.id)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            return redirect('course_detail', course_id=module.course.id)
    else:
        form = LessonForm()

    return render(request, 'courses/add_lesson.html', {
        'form': form,
        'module': module
    })

@login_required
@instructor_required
def create_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = SessionForm()

    return render(request, 'courses/create_session.html', {'form': form})

@login_required
def student_sessions(request):
    """
    Show all visible sessions and enrollment status for the logged-in student.
    """
    # Get all visible sessions
    sessions = Session.objects.filter(is_visible=True).order_by('date', 'start_time')

    # List of course IDs student is enrolled in
    enrolled_courses = list(
        Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    )

    return render(request, 'courses/student_sessions.html', {
        'sessions': sessions,
        'enrolled_courses': enrolled_courses
    })


@login_required
def enroll_course(request, course_id):
    """
    Enroll the logged-in student in a course if seats are available.
    """
    course = get_object_or_404(Course, id=course_id)

    if course.seats_left() <= 0:
        messages.error(request, "Course is full")
        return redirect('courses:student_sessions')

    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"You have been enrolled in {course.title}")
    #return redirect('courses:student_sessions')
    return redirect('courses:student_dashboard')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from courses.models import Course, Enrollment, Lesson

@login_required
def instructor_dashboard(request):
    # Get courses taught by instructor
    courses = Course.objects.filter(instructor=request.user).prefetch_related(
        'enrollments__student', 'sessions', 'enrollments__attendance_set'
    )

    for course in courses:
        total_sessions = course.sessions.count()
        total_lessons = Lesson.objects.filter(module__course=course).count()  # count lessons per course

        for enrollment in course.enrollments.all():
            # --- Attendance ---
            attended_sessions = enrollment.attendance_set.filter(present=True).count()
            enrollment.attended_sessions = attended_sessions
            enrollment.total_sessions = total_sessions
            enrollment.attendance_percent = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0

            # --- Progress (calculate on the fly) ---
            completed_lessons = getattr(enrollment, 'completed_lessons_count', 0)  # replace with your field
            enrollment.progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    # Dashboard totals
    students_count = Enrollment.objects.filter(course__in=courses).count()
    lessons_count = Lesson.objects.filter(module__course__in=courses).count()

    context = {
        'courses': courses,
        'students_count': students_count,
        'lessons_count': lessons_count,
    }
    return render(request, 'courses/instructor_dashboard.html', context)




@login_required
def student_dashboard(request):
    enrolled_courses = Enrollment.objects.filter(student=request.user)

    context = {
        'enrolled_courses': enrolled_courses,  # contains progress already
    }
    return render(request, 'courses/student_dashboard.html', context)


@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = Enrollment.objects.get(
        student=request.user,
        course=lesson.module.course
    )

    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()
    enrollment.update_progress()

    return redirect('lesson_detail', lesson_id=lesson.id)

from django.shortcuts import render, get_object_or_404, redirect
from courses.models import Session, Enrollment, Attendance

def mark_attendance(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    enrollments = session.course.enrollments.all()

    if request.method == "POST":
        # Iterate over all enrollments and mark attendance based on submitted form
        for enrollment in enrollments:
            present = request.POST.get(f'enrollment_{enrollment.id}') == 'on'  # checkbox value
            attendance, created = Attendance.objects.get_or_create(
                enrollment=enrollment,
                session=session
            )
            attendance.present = present
            attendance.status = 'completed' if present else 'absent'
            attendance.save()

            # Update progress for this enrollment
            enrollment.update_progress()

        return redirect('mark_attendance', session_id=session.id)  # refresh page after submission

    # GET request: precompute attendance status for display
    attendance_dict = {}
    for enrollment in enrollments:
        attendance = Attendance.objects.filter(enrollment=enrollment, session=session).first()
        attendance_dict[enrollment.id] = attendance.present if attendance else False

    context = {
        'session': session,
        'enrollments': enrollments,
        'attendance_dict': attendance_dict,
    }
    return render(request, 'courses/mark_attendance.html', context)


@login_required
def session_progress(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    # All students enrolled in the course
    enrollments = Enrollment.objects.filter(course=session.course)

    # All lessons in this session
    lessons = Lesson.objects.filter(module__course=session.course)
    total_lessons = lessons.count()

    students_progress = []

    for enrollment in enrollments:
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson__in=lessons,
            completed=True
        ).count()

        if total_lessons > 0:
            progress = int((completed_lessons / total_lessons) * 100)
        else:
            progress = 0

        students_progress.append({
            'student': enrollment.student,
            'progress': progress,
        })

    return render(request, 'courses/session_progress.html', {
        'session': session,
        'students_progress': students_progress,
    })

def python_course(request):
    return render(request, 'courses/python_course.html')

def ml_course(request):
    return render(request, 'courses/ml_course.html')

def dl_course(request):
    return render(request, 'courses/dl_course.html')

def powerbi_course(request):
    return render(request, 'courses/powerbi_course.html')




# courses/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Course, CourseRegistration

def courseEnroll(request):  # <--- Renamed to match views.courseEnroll in your URL
    """
    Handles guest/anonymous registration for a course.
    """
    if request.method == 'POST':
        # 1. Extract the data from the form fields
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        course_id = request.POST.get('course')
        preferred_date = request.POST.get('preferred_date')
        experience_level = request.POST.get('experience_level')
        comments = request.POST.get('comments')

        # 2. Match the selected course ID to an actual Course from the database
        try:
            selected_course = Course.objects.get(id=course_id)
            
            # 3. Create the registration record using your CourseRegistration model
            CourseRegistration.objects.create(
                full_name=full_name,
                phone=phone,
                email=email if email else None,  
                course=selected_course,
                preferred_date=preferred_date,
                experience_level=experience_level,
                comments=comments
            )
            
            messages.success(request, f"Thank you {full_name}! Your registration for '{selected_course.title}' has been received.")
            return redirect('courses:courseEnroll')
            
        except Course.DoesNotExist:
            messages.error(request, "The selected course could not be found.")
            return redirect('courses:courseEnroll')

    # GET logic: Pull all courses to populate the form's dropdown menu
    all_courses = Course.objects.all()
    return render(request, 'courses/course_enroll.html', {'courses': all_courses})





''' 



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CourseRegistration, Course

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CourseRegistration, Course

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CourseRegistration, Course
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CourseRegistration, Course

def courseEnroll(request):
    # Optional: pre-select course from GET parameter
    preselected_course = request.GET.get('course', '')

    if request.method == 'POST':
        course_title = request.POST.get('course')

        if not course_title:
            messages.error(request, "Please select a course.")
            return redirect('courses:courseEnroll')

        # Get Course object
        try:
            selected_course = Course.objects.get(title=course_title)
        except Course.DoesNotExist:
            messages.error(request, "Selected course not found!")
            return redirect('courses:courseEnroll')

        # Create registration
        CourseRegistration.objects.create(
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            course=selected_course,
            preferred_date=request.POST.get('preferred_date'),
            experience_level=request.POST.get('experience_level'),
            comments=request.POST.get('comments')
        )

        messages.success(request, "Enrollment submitted successfully!")
        return redirect('courses:courseEnroll')  # stay on same page

    return render(
        request,
        'courses/course_enroll.html',
        {'preselected_course': preselected_course}
    )

'''