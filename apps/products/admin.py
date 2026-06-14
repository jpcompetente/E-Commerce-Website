from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'category', 'price', 'status', 'stock', 'is_featured']
    list_filter = ['status', 'product_type', 'is_featured']
    search_fields = ['name', 'store__name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'order']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price', 'stock']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']