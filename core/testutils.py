from django.contrib.auth import get_user_model

from .models import UserProfile


def make_user(username, role, block='A'):
    # Unusable password: tests authenticate via force_login, and skipping hashing keeps them fast.
    user = get_user_model().objects.create_user(username=username)
    UserProfile.objects.create(user=user, role=role, block=block)
    return user
