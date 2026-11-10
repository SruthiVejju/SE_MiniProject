
from django.contrib import messages
from django.shortcuts import redirect, render

from core.models import UserProfile
from core.permissions import role_required

from .forms import AllocationForm
from .models import Allocation, Room
from .services import AllocationError, allocate_bed


@role_required(UserProfile.ADMIN)
def room_list(request):
    rooms = Room.objects.prefetch_related("beds").all()

    allocations = Allocation.objects.filter(
        is_active=True
    ).select_related("student", "bed", "bed__room")

    occupied_by = {
        allocation.bed_id: allocation.student.username
        for allocation in allocations
    }

    return render(request, "hostel/room_list.html", {
        "rooms": rooms,
        "occupied_by": occupied_by,
        "allocations": allocations,
    })


@role_required(UserProfile.ADMIN)
def allocate_room(request):
    if request.method == "POST":
        form = AllocationForm(request.POST)

        if form.is_valid():
            student = form.cleaned_data["student"]
            bed = form.cleaned_data["bed"]

            try:
                allocation = allocate_bed(student, bed.pk)
                messages.success(
                    request,
                    f"Bed allocated successfully to {student.username}."
                )
                return redirect("hostel:allocation_success", pk=allocation.pk)

            except AllocationError as error:
                form.add_error(None, str(error))

    else:
        form = AllocationForm()

    return render(request, "hostel/allocate.html", {
        "form": form
    })


@role_required(UserProfile.ADMIN)
def allocation_success(request, pk):
    from django.shortcuts import get_object_or_404

    allocation = get_object_or_404(
        Allocation.objects.select_related(
            "student", "bed", "bed__room"
        ),
        pk=pk
    )

    return render(request, "hostel/allocation_success.html", {
        "allocation": allocation
    })


@role_required(UserProfile.STUDENT)
def student_dashboard(request):
    allocation = (
        Allocation.objects
        .filter(
            student=request.user,
            is_active=True
        )
        .select_related("bed", "bed__room")
        .first()
    )

    fee_account = getattr(request.user, "fee_account", None)

    outstanding_dues = (
        fee_account.due if fee_account else None
    )

    return render(
        request,
        "hostel/student_dashboard.html",
        {
            "allocation": allocation,
            "fee_account": fee_account,
            "outstanding_dues": outstanding_dues,
        }
    )
