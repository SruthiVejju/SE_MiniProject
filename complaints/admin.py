from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'complaint_id',
        'student',
        'category',
        'created_at',
    )
    list_filter = ('category', 'created_at')
    search_fields = ('complaint_id', 'student__username', 'description')
    readonly_fields = ('complaint_id', 'created_at')