from django.conf import settings
from django.db import models


class LeaveRequest(models.Model):
    PENDING, APPROVED, REJECTED = 'pending', 'approved', 'rejected'
    STATUS_CHOICES = [(PENDING, 'Pending'), (APPROVED, 'Approved'), (REJECTED, 'Rejected')]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    block = models.CharField(max_length=50, db_index=True)
    warden = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='assigned_leave_requests')
    destination = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='decided_leave_requests')
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Leave #{self.pk} {self.student} -> {self.destination} ({self.status})'
