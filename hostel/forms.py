
from django import forms
from django.contrib.auth import get_user_model

from core.models import UserProfile
from .models import Allocation, Bed


class AllocationForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        label="Select Student"
    )

    bed = forms.ModelChoiceField(
        queryset=Bed.objects.none(),
        label="Select Available Bed"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allocated_students = Allocation.objects.filter(
            is_active=True
        ).values_list("student_id", flat=True)

        self.fields["student"].queryset = (
            get_user_model().objects.filter(
                profile__role=UserProfile.STUDENT
            )
            .exclude(pk__in=allocated_students)
            .order_by("username")
        )

        allocated_beds = Allocation.objects.filter(
            is_active=True
        ).values_list("bed_id", flat=True)

        self.fields["bed"].queryset = (
            Bed.objects.filter(is_occupied=False)
            .exclude(pk__in=allocated_beds)
            .select_related("room")
            .order_by("room__block", "room__room_number", "bed_number")
        )
