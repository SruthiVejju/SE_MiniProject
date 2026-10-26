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
