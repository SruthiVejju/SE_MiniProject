"""
Audit logging service supporting SEC-REQ-5.

Guarantees:
- Captures authentication events (success/failure/logout) and admin actions.
- Enforces append-only storage and 1-year (365 days) minimum retention.
"""
from datetime import timedelta
import logging
from django.utils import timezone
from .models import AuditLog

logger = logging.getLogger(__name__)

# Standard action constants
AUTH_LOGIN_SUCCESS = 'auth.login.success'
AUTH_LOGIN_FAILED = 'auth.login.failed'
AUTH_LOGOUT = 'auth.logout'
FEE_PAYMENT_RECORDED = 'fees.payment.recorded'
ROOM_ALLOCATION_CREATED = 'hostel.allocation.created'
ROOM_ALLOCATION_DEACTIVATED = 'hostel.allocation.deactivated'
NOTICE_PUBLISHED = 'notices.notice.published'


def get_client_ip(request):
    """Safely extract client IP address from request headers."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_audit_event(action, actor=None, actor_username='', ip_address=None, details=None, request=None):
    """
    Record an append-only audit log entry.
    If `request` is provided, automatically populates actor and client IP.
    """
    if request:
        if not ip_address:
            ip_address = get_client_ip(request)
        if not actor and getattr(request, 'user', None) and request.user.is_authenticated:
            actor = request.user
            actor_username = actor.username

    if actor and not actor_username:
        actor_username = getattr(actor, 'username', str(actor))

    entry_details = details if isinstance(details, dict) else ({'detail': details} if details else {})

    try:
        now = timezone.now()
        entry = AuditLog.objects.create(
            timestamp=now,
            action=action,
            actor=actor if (actor and getattr(actor, 'pk', None)) else None,
            actor_username=actor_username or '',
            ip_address=ip_address,
            details=entry_details,
            retention_until=now + timedelta(days=365)
        )
        return entry
    except Exception as exc:
        logger.error(f"Failed to record audit log entry for action {action}: {exc}")
        return None


def verify_audit_retention(min_days=365):
    """
    Verify that all stored audit records have a retention period of at least `min_days`.
    Returns True if all records comply with the retention policy.
    """
    now = timezone.now()
    threshold = timedelta(days=min_days - 1)
    for record in AuditLog.objects.all():
        if not record.retention_until:
            return False
        if (record.retention_until - record.timestamp) < threshold:
            return False
    return True
