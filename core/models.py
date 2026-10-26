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
