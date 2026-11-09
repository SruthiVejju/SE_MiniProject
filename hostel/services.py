
from django.db import IntegrityError, OperationalError, transaction

from core.models import UserProfile
from .models import Allocation, Bed


class AllocationError(Exception):
    pass


def allocate_bed(student, bed_id):
    """
    Allocate a vacant bed to a registered student.
    Prevent duplicate student and bed allocations.
    """

    if not UserProfile.objects.filter(
        user=student,
        role=UserProfile.STUDENT
    ).exists():
        raise AllocationError(
            "Only registered students can be allocated beds."
        )

    try:
        with transaction.atomic():
            bed = (
                Bed.objects.select_for_update()
                .select_related("room")
                .get(pk=bed_id)
            )

            if bed.is_occupied or Allocation.objects.filter(
                bed=bed, is_active=True
            ).exists():
                raise AllocationError(
                    "This bed is already occupied."
                )

            if Allocation.objects.filter(
                student=student, is_active=True
            ).exists():
                raise AllocationError(
                    "This student already has an active allocation."
                )

            allocation = Allocation.objects.create(
                student=student,
                bed=bed,
                is_active=True
            )

            bed.is_occupied = True
            bed.save(update_fields=["is_occupied"])

            return allocation

    except Bed.DoesNotExist:
        raise AllocationError("Selected bed does not exist.")
    except IntegrityError:
        raise AllocationError(
            "Allocation conflict. The bed or student is already allocated."
        )
    except OperationalError:
        raise AllocationError(
            "Database is busy. Please retry the allocation."
        )
