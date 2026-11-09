
from django.conf import settings
from django.db import models
from django.db.models import Q


class Room(models.Model):
    block = models.CharField(max_length=50)
    room_number = models.CharField(max_length=20)
    floor = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["block", "room_number"],
                name="unique_room_per_block"
            )
        ]
        ordering = ["block", "room_number"]

    def __str__(self):
        return f"Block {self.block} - Room {self.room_number}"


class Bed(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="beds"
    )
    bed_number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room", "bed_number"],
                name="unique_bed_per_room"
            )
        ]
        ordering = ["room", "bed_number"]

    def __str__(self):
        return f"{self.room} - Bed {self.bed_number}"


class Allocation(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="hostel_allocations"
    )
    bed = models.ForeignKey(
        Bed,
        on_delete=models.PROTECT,
        related_name="allocations"
    )
    allocated_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bed"],
                condition=Q(is_active=True),
                name="unique_active_bed_allocation"
            ),
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(is_active=True),
                name="unique_active_student_allocation"
            ),
        ]
        ordering = ["-allocated_at"]

    def __str__(self):
        return f"{self.student.username} - {self.bed}"
