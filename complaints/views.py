from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import UserProfile
from core.permissions import role_required

from .forms import ComplaintForm, ComplaintUpdateForm
from .models import Complaint


@role_required(UserProfile.STUDENT)
def submit_complaint(request):
    form = ComplaintForm(
        request.POST if request.method == 'POST' else None
    )

    if request.method == 'POST' and form.is_valid():
        complaint = form.save(commit=False)
        complaint.student = request.user
        complaint.save()

        return render(
            request,
            'complaints/success.html',
            {'complaint': complaint}
        )

    return render(
        request,
        'complaints/submit.html',
        {'form': form}
    )


@role_required(UserProfile.WARDEN)
def complaint_list(request):
    complaints = Complaint.objects.filter(
        student__profile__block=request.profile.block
    ).select_related('student', 'student__profile')

    return render(
        request,
        'complaints/warden_list.html',
        {'complaints': complaints}
    )


@role_required(UserProfile.WARDEN)
@require_POST
def update_complaint(request, pk):
    complaint = get_object_or_404(
        Complaint.objects.filter(
            student__profile__block=request.profile.block
        ),
        pk=pk
    )

    form = ComplaintUpdateForm(request.POST, instance=complaint)

    if form.is_valid():
        form.save()
        messages.success(request, 'Complaint updated successfully.')
    else:
        messages.error(request, 'Invalid complaint status or remark.')

    return redirect('complaint-list')