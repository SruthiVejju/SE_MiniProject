import json
from functools import wraps
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from core.models import UserProfile
from core.permissions import get_profile


def api_error_response(message, status=400, code=None):
    payload = {"error": message}
    if code:
        payload["code"] = code
    return JsonResponse(payload, status=status)


def api_login_required(view_func):
    """Ensure API caller is authenticated, returning JSON 401 instead of redirect."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return api_error_response("Authentication credentials were not provided or are invalid.", status=401, code="UNAUTHORIZED")
        return view_func(request, *args, **kwargs)
    return wrapper


def api_role_required(*roles):
    """Enforce RBAC for API endpoints returning JSON 403 on permission denial."""
    def decorator(view_func):
        @wraps(view_func)
        @api_login_required
        def wrapper(request, *args, **kwargs):
            profile = get_profile(request.user)
            if profile is None or profile.role not in roles:
                return api_error_response(
                    f"Forbidden: Access requires one of the following roles: {', '.join(roles)}.",
                    status=403,
                    code="FORBIDDEN"
                )
            request.profile = profile
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def parse_json_body(request):
    """Safely parse request.body as JSON dictionary."""
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except Exception:
        return None
