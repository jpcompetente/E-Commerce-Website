from django.contrib import admin
from .models import Review, ReviewReply, StoreReview

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'product', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ['review', 'author', 'created_at']

@admin.register(StoreReview)
class StoreReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'store', 'rating', 'created_at']