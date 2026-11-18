from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.audit import FEE_PAYMENT_RECORDED, log_audit_event
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

    log_audit_event(
        FEE_PAYMENT_RECORDED,
        actor=admin_user,
        actor_username=getattr(admin_user, 'username', '') if admin_user else '',
        details={
            'account_id': account.pk,
            'student': str(account.student.username),
            'amount': str(amount),
            'mode': mode,
            'receipt_number': payment.receipt_number,
        }
    )

    return payment
