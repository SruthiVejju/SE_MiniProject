from django.contrib import admin

from .models import AuditLog, Notification, UserProfile

admin.site.register(UserProfile)
admin.site.register(Notification)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'actor_username', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor_username', 'action', 'ip_address')
    readonly_fields = ('timestamp', 'action', 'actor', 'actor_username', 'ip_address', 'details', 'retention_until')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

