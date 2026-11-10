from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

from .forms import StudentRegistrationForm
from .models import UserProfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .permissions import get_profile


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
