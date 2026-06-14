from django.contrib import admin
from .models import Payment, VendorPayout

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'status', 'amount', 'created_at']
    list_filter = ['method', 'status']

@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ['store', 'amount', 'commission_deducted', 'status', 'paid_at']
    list_filter = ['status']