from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    order_item = models.OneToOneField('orders.OrderItem', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100, blank=True)
    body = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'reviewer']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.email} → {self.product.name} ({self.rating}★)"

class ReviewReply(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='reply')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to review #{self.review.id}"

class StoreReview(models.Model):
    store = models.ForeignKey('vendors.Store', on_delete=models.CASCADE, related_name='store_reviews')
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='store_review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.email} → {self.store.name} ({self.rating}★)"