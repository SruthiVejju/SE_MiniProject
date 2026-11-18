
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from core.models import UserProfile
from core.permissions import role_required

from .forms import AllocationForm
from .models import Allocation, Room
from .reports import generate_occupancy_pdf, get_occupancy_data
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
                allocation = allocate_bed(student, bed.pk, admin_user=request.user)
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


@role_required(UserProfile.ADMIN)
def occupancy_report(request, format=None):
    """Generate hostel occupancy report with optional PDF export (FR-12)."""
    data = get_occupancy_data()

    if format == "pdf" or request.GET.get("format") == "pdf":
        pdf_bytes = generate_occupancy_pdf(data)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        filename = f"hostel_occupancy_report_{data['generated_at']:%Y%m%d}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    return render(request, "hostel/occupancy_report.html", {
        "report": data
    })

