from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_block', 'posted_by', 'created_at')
    list_filter = ('target_block', 'created_at')
    search_fields = ('title', 'content', 'posted_by__username')
