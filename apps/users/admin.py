from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DriverProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone_number']
    
    fieldsets = UserAdmin.fieldsets + (
        ('追加情報', {'fields': ('phone_number', 'user_type', 'is_verified')}),
    )


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_type', 'is_available', 'created_at']
    list_filter = ['vehicle_type', 'is_available', 'created_at']
    search_fields = ['user__username', 'user__email', 'license_number', 'vehicle_number']
