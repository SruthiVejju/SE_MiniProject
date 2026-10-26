from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import UserProfile
from core.permissions import role_required

from .forms import LeaveRequestForm
from .models import LeaveRequest
from .services import decide_leave, submit_leave


@role_required(UserProfile.STUDENT)
def submit(request):
    form = LeaveRequestForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        submit_leave(request.profile, form)
        messages.success(request, 'Leave request submitted.')
        return redirect('leave-mine')
    return render(request, 'leaves/submit.html', {'form': form})


@role_required(UserProfile.STUDENT)
def my_requests(request):
    leaves = LeaveRequest.objects.filter(student=request.user)
    return render(request, 'leaves/mine.html', {'leaves': leaves})


@role_required(UserProfile.WARDEN)
def pending(request):
    leaves = LeaveRequest.objects.filter(block=request.profile.block)
    return render(request, 'leaves/pending.html', {'leaves': leaves})


@role_required(UserProfile.WARDEN)
@require_POST
def decide(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if leave.block != request.profile.block:
        raise PermissionDenied
    action = request.POST.get('action')
    if action not in ('approve', 'reject'):
        messages.error(request, 'Invalid action.')
    else:
        try:
            decide_leave(leave, request.user, approve=(action == 'approve'))
            messages.success(request, f'Request {leave.status}.')
        except ValueError as exc:
            messages.error(request, str(exc))
    return redirect('leave-pending')
