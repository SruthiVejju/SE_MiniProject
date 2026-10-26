from decimal import Decimal

from django.conf import settings
from django.db import models


class FeeAccount(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fee_account')
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    @property
    def due(self):
        return self.total_fee - self.amount_paid

    def __str__(self):
        return f'{self.student}: due {self.due}'


class FeePayment(models.Model):
    CASH, ONLINE = 'cash', 'online'
    MODE_CHOICES = [(CASH, 'Cash'), (ONLINE, 'Online')]

    account = models.ForeignKey(FeeAccount, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    reference = models.CharField(max_length=64, blank=True)
    receipt_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f'{self.receipt_number}: {self.amount} ({self.mode})'
