from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from accounts.models import profile


# Create your views here.

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role')
        if form.is_valid():
            user = form.save()
            user.profile.role = role
            user.profile.save()
            login(request,user)
            return redirect('role_redirect')
    else:
        form = UserCreationForm()
    return  render(request,'accounts/register.html',{'form':form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # role-based redirect
            role = user.profile.role 

            if role == 'STUDENT':
                return redirect('student_dashboard')
            elif role == 'INSTRUCTOR':
                return redirect('instructor_dashboard')
            else:
                return redirect('/admin/')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

# logout view
def logout_view(request):
    logout(request)
    return redirect('login')


#Redirect View (Role-based)

@login_required
def role_redirect_view(request):
    role = request.user.profile.role

    if role == 'ADMIN':
        return redirect('/admin/')
    elif role == 'INSTRUCTOR':
        return redirect('instructor_dashboard')
    elif role == 'STUDENT':
        return redirect('student_dashboard')
    else:
        return redirect('login')

@login_required
def student_dashboard(request):
    if request.user.profile.role != 'STUDENT':
        return redirect('role_redirect')
    return render(request, 'accounts/student_dashboard.html')


@login_required
def instructor_dashboard(request):
    if request.user.profile.role != 'INSTRUCTOR':
        return redirect('role_redirect')
    return render(request, 'accounts/instructor_dashboard.html')
