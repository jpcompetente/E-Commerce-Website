from django.db import models
from django.conf import settings
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    DRAFT = 'draft'
    ACTIVE = 'active'
    PAUSED = 'paused'
    SOLD_OUT = 'sold_out'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'), (ACTIVE, 'Active'),
        (PAUSED, 'Paused'), (SOLD_OUT, 'Sold Out'),
    ]
    PHYSICAL = 'physical'
    DIGITAL = 'digital'
    SERVICE = 'service'
    TYPE_CHOICES = [
        (PHYSICAL, 'Physical'), (DIGITAL, 'Digital'), (SERVICE, 'Service'),
    ]

    store = models.ForeignKey('vendors.Store', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=PHYSICAL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    stock = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    digital_file = models.FileField(upload_to='digital_products/', blank=True, null=True)
    tags = TaggableManager(blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    views = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock > 0

    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='variants/', blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def effective_price(self):
        return self.price if self.price else self.product.price


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.email} → {self.product.name}"