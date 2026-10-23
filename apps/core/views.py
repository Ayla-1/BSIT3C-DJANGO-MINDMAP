from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from apps.core.models import UserProfile

User = get_user_model()

# Import models for profile view
from apps.users.models import Teacher, Student, Subject, Grade
from django.db.models import Avg

MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION = timedelta(minutes=1)
INVALID_LOGIN_MESSAGE = 'Invalid username or password.'
LOCKED_MESSAGE = 'Too many failed attempts. Locked for 1 minute.'


def _reset_lock_state(request):
    request.session['failed_attempts'] = 0
    request.session['lock_time'] = None


def _get_lock_state(request):
    failed_attempts = request.session.get('failed_attempts', 0)
    lock_time = request.session.get('lock_time')

    if not lock_time:
        return failed_attempts, None

    try:
        unlock_time = timezone.datetime.fromisoformat(lock_time)
    except (TypeError, ValueError):
        _reset_lock_state(request)
        return 0, None

    if timezone.now() < unlock_time:
        remaining = int((unlock_time - timezone.now()).total_seconds())
        return failed_attempts, remaining

    _reset_lock_state(request)
    return 0, None


def _set_lock_state(request):
    lock_until = timezone.now() + LOCK_DURATION
    request.session['failed_attempts'] = MAX_FAILED_ATTEMPTS
    request.session['lock_time'] = lock_until.isoformat()
    return int(LOCK_DURATION.total_seconds())


def _validate_registration_data(data):
    errors = {}

    username = data.get('username', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not username:
        errors['username'] = 'Username is required.'
    elif User.objects.filter(username=username).exists():
        errors['username'] = 'Username already taken.'

    if not first_name:
        errors['first_name'] = 'First name is required.'

    if not last_name:
        errors['last_name'] = 'Last name is required.'

    if not email:
        errors['email'] = 'Email is required.'
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Enter a valid email address.'
        else:
            if User.objects.filter(email=email).exists():
                errors['email'] = 'Email already registered.'

    if not password:
        errors['password'] = 'Password is required.'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters.'
    else:
        try:
            validate_password(password)
        except ValidationError as exc:
            errors['password'] = ' '.join(exc.messages)

    if password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'

    return errors


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    failed_attempts, remaining = _get_lock_state(request)
    if remaining is not None:
        messages.error(request, f'Too many failed attempts. Try again in {remaining} seconds.')
        return render(request, 'auth/login.html', {'locked': True, 'remaining': remaining})

    if request.method == 'GET':
        return render(request, 'auth/login.html')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        _reset_lock_state(request)
        login(request, user)
        # Redirect based on user role
        try:
            profile = user.profile
            if profile.is_admin():
                return redirect('admin_dashboard')
            elif profile.is_teacher():
                return redirect('teacher_dashboard')
            elif profile.is_student():
                return redirect('student_dashboard')
        except UserProfile.DoesNotExist:
            # If no profile exists, redirect to general dashboard
            return redirect('dashboard')

    failed_attempts += 1
    request.session['failed_attempts'] = failed_attempts
    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        remaining = _set_lock_state(request)
        messages.error(request, LOCKED_MESSAGE)
        return render(request, 'auth/login.html', {'locked': True, 'remaining': remaining})

    remaining_attempts = MAX_FAILED_ATTEMPTS - failed_attempts
    messages.error(request, f'{INVALID_LOGIN_MESSAGE} {remaining_attempts} attempts remaining.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    """Main dashboard redirector"""
    try:
        profile = request.user.profile
        if profile.is_admin():
            return redirect('admin_dashboard')
        elif profile.is_teacher():
            return redirect('teacher_dashboard')
        elif profile.is_student():
            return redirect('student_dashboard')
    except UserProfile.DoesNotExist:
        pass
    return render(request, 'home.html')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'GET':
        return render(request, 'auth/register.html')

    form_data = {
        'username': request.POST.get('username', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'email': request.POST.get('email', ''),
        'password': request.POST.get('password', ''),
        'confirm_password': request.POST.get('confirm_password', ''),
    }

    errors = _validate_registration_data(form_data)
    if errors:
        return render(request, 'auth/register.html', {'errors': errors, 'form_data': form_data})

    user = User.objects.create_user(
        username=form_data['username'].strip(),
        first_name=form_data['first_name'].strip(),
        last_name=form_data['last_name'].strip(),
        email=form_data['email'].strip(),
        password=form_data['password'],
    )
    login(request, user)
    return redirect('dashboard')


def test_login_page(request):
    """Test login page to check session and test accounts"""
    return render(request, 'test_login.html')


def test_dropdown(request):
    """Test dropdown functionality"""
    return render(request, 'test_dropdown.html')


@login_required(login_url='login')
def user_profile(request):
    """User profile page - shows different info based on role"""
    
    # Handle password change
    if request.method == 'POST' and request.POST.get('action') == 'change_password':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verify current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('user_profile')
        
        # Verify new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('user_profile')
        
        # Verify password length
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('user_profile')
        
        # Change password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('user_profile')
    
    try:
        profile = request.user.profile
        role = profile.role
        
        context = {
            'profile': profile,
            'role': role,
        }
        
        # Add role-specific information
        if role == 'teacher':
            try:
                username = request.user.username
                teacher = Teacher.objects.get(email__startswith=username)
                context['teacher'] = teacher
                context['my_subjects'] = Subject.objects.filter(teacher=teacher)
            except Teacher.DoesNotExist:
                pass
                
        elif role == 'student':
            try:
                student = Student.objects.get(student_number=request.user.username)
                context['student'] = student
                # Get statistics
                all_grades = Grade.objects.filter(student=student, final_grade__isnull=False)
                context['total_grades'] = all_grades.count()
                context['avg_grade'] = all_grades.aggregate(Avg('final_grade'))['final_grade__avg']
            except Student.DoesNotExist:
                pass
        
        return render(request, 'profile.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')
