from django.db import models
from django.conf import settings

class Payment(models.Model):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (SUCCESS, 'Success'),
        (FAILED, 'Failed'), (REFUNDED, 'Refunded'),
    ]
    STRIPE = 'stripe'
    GCASH = 'gcash'
    COD = 'cod'
    METHOD_CHOICES = [
        (STRIPE, 'Stripe'), (GCASH, 'GCash'), (COD, 'Cash on Delivery'),
    ]
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.method} ({self.status})"

class VendorPayout(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    PAID = 'paid'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (PROCESSING, 'Processing'), (PAID, 'Paid'),
    ]
    store = models.ForeignKey('vendors.Store', on_delete=models.CASCADE, related_name='payouts')
    sub_order = models.OneToOneField('orders.SubOrder', on_delete=models.CASCADE, related_name='payout')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_deducted = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payout to {self.store.name} - ₱{self.amount}"