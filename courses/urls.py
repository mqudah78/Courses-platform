from django.urls import path
from . import views

app_name = 'courses'  

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.course_create, name='course_create'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),

    path('<int:course_id>/add-module/', views.add_module, name='add_module'),
    path('module/<int:module_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
       
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/student/', views.student_sessions, name='student_sessions'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('instructor-dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    path('lessons/<int:lesson_id>/complete/',views.mark_lesson_complete,name='mark_lesson_complete'),

    path('sessions/<int:session_id>/attendance/',views.mark_attendance,name='mark_attendance'),
    path('sessions/<int:session_id>/progress/',views.session_progress,name='session_progress'),

    path('python/', views.python_course, name='python_course'),
    path('ml/', views.ml_course, name='ml_course'),
    path('dl/', views.dl_course, name='dl_course'),
    path('powerbi/', views.powerbi_course, name='powerbi_course'),

    path('enroll/', views.courseEnroll, name='courseEnroll'),

]


