from django.contrib import admin
from .models import Store, VendorApplication, StorePolicy

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'is_student', 'rating', 'total_sales']
    list_filter = ['status', 'is_student']
    search_fields = ['name', 'owner__email']

@admin.register(VendorApplication)
class VendorApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'store_name', 'business_type', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'store_name']

@admin.register(StorePolicy)
class StorePolicyAdmin(admin.ModelAdmin):
    list_display = ['store', 'updated_at']