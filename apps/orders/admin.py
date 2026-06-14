from django.contrib import admin
from .models import Cart, CartItem, Order, SubOrder, OrderItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'status', 'total', 'created_at']
    list_filter = ['status']
    search_fields = ['order_number', 'buyer__email']

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ['order', 'store', 'status', 'subtotal', 'vendor_earning']
    list_filter = ['status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['sub_order', 'product', 'quantity', 'price']