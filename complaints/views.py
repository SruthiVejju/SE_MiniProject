from django.shortcuts import redirect, render

from core.models import UserProfile
from core.permissions import role_required

from .forms import ComplaintForm


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