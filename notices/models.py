from django.conf import settings
from django.db import models
from core.models import Notification, UserProfile


class Notice(models.Model):
    """
    Hostel notice/announcement entity (FR-11).
    Allows Admins to broadcast notices to all students or target a specific block.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_block = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Leave blank to target all students, or specify block name (e.g. 'A')."
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_notices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = f"Block {self.target_block}" if self.target_block else "All Students"
        return f"{self.title} ({target})"

    @property
    def is_general(self):
        return not self.target_block or self.target_block.strip().upper() == 'ALL'

    def is_visible_to(self, user):
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, 'profile', None)
        if not profile:
            return False
        if profile.role in [UserProfile.ADMIN, UserProfile.WARDEN]:
            return True
        if profile.role == UserProfile.STUDENT:
            if self.is_general:
                return True
            return bool(
                profile.block and
                profile.block.strip().lower() == self.target_block.strip().lower()
            )
        return False

    def notify_target_students(self):
        """Dispatch in-app notifications to targeted students for this notice."""
        students_qs = UserProfile.objects.filter(role=UserProfile.STUDENT).select_related('user')
        if not self.is_general:
            students_qs = students_qs.filter(block__iexact=self.target_block.strip())

        notifications = [
            Notification(
                user=profile.user,
                message=f"Notice: {self.title[:80]}"
            )
            for profile in students_qs
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)
