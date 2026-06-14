from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'role', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['email', 'username']
    fieldsets = UserAdmin.fieldsets + (
        ('Marketplace Info', {'fields': ('role', 'avatar', 'bio', 'phone', 'is_verified')}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'full_name', 'city', 'is_default']
    search_fields = ['user__email', 'full_name', 'city']