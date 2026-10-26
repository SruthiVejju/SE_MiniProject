from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import UserProfile


def get_profile(user):
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        return None


def role_required(*roles):
    """Allow only authenticated users whose profile role is in `roles` (SEC-REQ-2)."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = get_profile(request.user)
            if profile is None or profile.role not in roles:
                raise PermissionDenied
            request.profile = profile
            return view(request, *args, **kwargs)

        return wrapper

    return decorator
