from django.conf import settings
from django.db import models


class Visitor(models.Model):
    name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=200)
    host_student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visitors')
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name='logged_visitors')

    class Meta:
        ordering = ['-entry_time']

    @property
    def is_inside(self):
        return self.exit_time is None

    def __str__(self):
        return f'{self.name} visiting {self.host_student}'
