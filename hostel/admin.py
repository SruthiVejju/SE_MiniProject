
from django.contrib import admin
from .models import Room, Bed, Allocation


class BedInline(admin.TabularInline):
    model = Bed
    extra = 2


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("block", "room_number", "floor")
    search_fields = ("block", "room_number")
    inlines = [BedInline]


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("bed_number", "room", "is_occupied")
    list_filter = ("is_occupied", "room__block")


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = (
        "student", "bed", "allocated_at", "is_active"
    )
    list_filter = ("is_active",)
    readonly_fields = (
        "student", "bed", "allocated_at", "is_active"
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
