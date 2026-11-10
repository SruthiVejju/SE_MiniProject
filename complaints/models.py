import uuid

from django.conf import settings
from django.db import models


class Complaint(models.Model):
    ELECTRICAL = 'electrical'
    PLUMBING = 'plumbing'
    CLEANING = 'cleaning'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (ELECTRICAL, 'Electrical'),
        (PLUMBING, 'Plumbing'),
        (CLEANING, 'Cleaning'),
        (OTHER, 'Other'),
    ]

    complaint_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='maintenance_complaints'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Complaint {self.complaint_id} - {self.student}'