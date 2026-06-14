from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Store(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'), (SUSPENDED, 'Suspended'),
    ]

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='store_banners/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    is_student = models.BooleanField(default=False)
    school = models.CharField(max_length=255, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_sales = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VendorApplication(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (APPROVED, 'Approved'), (REJECTED, 'Rejected'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_application')
    store_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    description = models.TextField()
    is_student = models.BooleanField(default=False)
    school = models.CharField(max_length=255, blank=True)
    id_document = models.FileField(upload_to='vendor_documents/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.store_name}"


class StorePolicy(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='policy')
    return_policy = models.TextField(blank=True)
    shipping_policy = models.TextField(blank=True)
    privacy_policy = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Policy for {self.store.name}"