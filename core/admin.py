from django.contrib import admin

from .models import AdminProfile


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('is_active', 'role', 'created_at')
    search_fields = ('full_name', 'email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
