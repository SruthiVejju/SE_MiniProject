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
    # Student registration details
    full_name = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)

# Account security and login tracking
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

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

class AuditLog(models.Model):
    """Records authentication and registration events."""

    REGISTRATION = 'registration'
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILURE = 'login_failure'
    LOGOUT = 'logout'

    EVENT_CHOICES = [
        (REGISTRATION, 'Registration'),
        (LOGIN_SUCCESS, 'Login Success'),
        (LOGIN_FAILURE, 'Login Failure'),
        (LOGOUT, 'Logout'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    event = models.CharField(
        max_length=20,
        choices=EVENT_CHOICES
    )

    identifier = models.CharField(max_length=150, blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event} - {self.identifier} - {self.created_at}'
