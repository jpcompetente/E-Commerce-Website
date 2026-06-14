from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    BUYER = 'buyer'
    VENDOR = 'vendor'
    ROLE_CHOICES = [(BUYER, 'Buyer'), (VENDOR, 'Vendor')]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BUYER)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_vendor(self):
        return self.role == self.VENDOR

    @property
    def has_store(self):
        return hasattr(self, 'store')

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Philippines')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.label} - {self.full_name}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)