from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import FeeAccount, FeePayment


class PaymentError(Exception):
    pass


@transaction.atomic
def record_payment(account_id, amount, mode, reference, admin_user):
    """Record a payment, update the fee account and issue a unique receipt number."""
    account = FeeAccount.objects.select_for_update().get(pk=account_id)
    amount = Decimal(amount)
    if amount <= 0:
        raise PaymentError('Amount must be greater than zero.')
    if amount > account.due:
        raise PaymentError('Amount exceeds the outstanding due.')
    if mode == FeePayment.ONLINE and not reference:
        raise PaymentError('Online payments require a gateway transaction reference.')

    payment = FeePayment.objects.create(
        account=account, amount=amount, mode=mode,
        reference=reference, recorded_by=admin_user)
    # Primary key is unique, so the derived receipt number is too.
    payment.receipt_number = f'RCPT-{timezone.localdate():%Y%m%d}-{payment.pk:06d}'
    payment.save(update_fields=['receipt_number'])

    account.amount_paid += amount
    account.save(update_fields=['amount_paid'])
    return payment
