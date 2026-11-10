from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Role and hostel block of a user, used for RBAC and request routing."""

    STUDENT, WARDEN, ADMIN, SECURITY = 'student', 'warden', 'admin', 'security'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (WARDEN, 'Warden'),
        (ADMIN, 'Admin'),
        (SECURITY, 'Security Guard'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    block = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.user} ({self.role}, block {self.block or "-"})'


class Notification(models.Model):
    """In-app notification shown to a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user}: {self.message}'


from django.utils import timezone
from datetime import timedelta


class LoginAttempt(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_attempt'
    )
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    def is_locked(self):
        return self.locked_until is not None and self.locked_until > timezone.now()

    def record_failure(self):
        self.failed_attempts += 1

        if self.failed_attempts >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=15)
            self.failed_attempts = 0

        self.save()

    def reset(self):
        self.failed_attempts = 0
        self.locked_until = None
        self.save()

    def __str__(self):
        return f'{self.user.username}: {self.failed_attempts} failed attempts'
