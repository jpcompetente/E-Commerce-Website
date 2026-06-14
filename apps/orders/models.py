from django.db import models
from django.conf import settings
import uuid


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user.email if self.user else self.session_key})"

    @property
    def item_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        price = self.variant.effective_price if self.variant else self.product.price
        return price * self.quantity


class Order(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (CONFIRMED, 'Confirmed'),
        (SHIPPED, 'Shipped'), (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'), (REFUNDED, 'Refunded'),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    shipping_address = models.JSONField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class SubOrder(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (CONFIRMED, 'Confirmed'),
        (SHIPPED, 'Shipped'), (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sub_orders')
    store = models.ForeignKey('vendors.Store', on_delete=models.CASCADE, related_name='sub_orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    vendor_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.order.order_number} - {self.store.name}"


class OrderItem(models.Model):
    sub_order = models.ForeignKey(SubOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity