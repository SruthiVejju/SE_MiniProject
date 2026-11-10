from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

from .forms import StudentRegistrationForm
from .models import UserProfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .permissions import get_profile

from django.contrib.auth import authenticate, logout
from django.utils import timezone
from .models import LoginAttempt
from .login_forms import HMSLoginForm

from django.contrib.auth import get_user_model


@login_required
def home(request):
    profile = get_profile(request.user)
    return render(request, 'home.html', {
        'role': profile.role if profile else None,
        'notifications': request.user.notifications.all()[:20],
    })


@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('home')

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()

                UserProfile.objects.create(
                    user=user,
                    role=UserProfile.STUDENT,
                    block=form.cleaned_data['block']
                )

            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})



def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        User = get_user_model()

        user = User.objects.filter(username__iexact=username).first()

        if user:
            attempt, _ = LoginAttempt.objects.get_or_create(user=user)

            if attempt.is_locked():
                remaining = attempt.locked_until - timezone.now()
                minutes = max(1, int(remaining.total_seconds() // 60) + 1)

                messages.error(
                    request,
                    f'Account locked. Try again in approximately {minutes} minute(s).'
                )
                return render(
                    request, 'login.html',
                    {'form': HMSLoginForm(request)}
                )

        form = HMSLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            attempt, _ = LoginAttempt.objects.get_or_create(user=user)
            attempt.reset()

            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')

        if user:
            attempt, _ = LoginAttempt.objects.get_or_create(user=user)
            attempt.record_failure()

            if attempt.is_locked():
                messages.error(
                    request,
                    'Five failed attempts. Your account is locked for 15 minutes.'
                )
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')

    else:
        form = HMSLoginForm(request)

    return render(request, 'login.html', {'form': form})


def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')

    return redirect('home')
