from django.db import transaction
from django.utils import timezone

from core.models import Notification, UserProfile

from .models import LeaveRequest


def find_warden(block):
    """Return the warden user assigned to `block`, or None."""
    profile = (UserProfile.objects
               .filter(role=UserProfile.WARDEN, block=block).select_related('user').first())
    return profile.user if profile else None


@transaction.atomic
def submit_leave(student_profile, form):
    """Persist a validated leave form, routed to the student's block warden."""
    leave = form.save(commit=False)
    leave.student = student_profile.user
    leave.block = student_profile.block
    leave.warden = find_warden(student_profile.block)
    leave.save()
    if leave.warden:
        Notification.objects.create(
            user=leave.warden,
            message=f'New leave request from {leave.student} to {leave.destination}.')
    return leave


@transaction.atomic
def decide_leave(leave, warden_user, approve):
    """Approve/reject a pending request and notify the student immediately."""
    if leave.status != LeaveRequest.PENDING:
        raise ValueError('Only pending requests can be decided.')
    leave.status = LeaveRequest.APPROVED if approve else LeaveRequest.REJECTED
    leave.decided_by = warden_user
    leave.decided_at = timezone.now()
    leave.save()
    Notification.objects.create(
        user=leave.student,
        message=(f'Your leave request to {leave.destination} '
                 f'({leave.from_date} - {leave.to_date}) was {leave.status}.'))
    return leave
