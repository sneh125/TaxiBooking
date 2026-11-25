from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'license_number', 'mobile', 'created_at')
    search_fields = ('name', 'email', 'license_number', 'mobile')
