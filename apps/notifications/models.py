from django.db import models
from django.conf import settings


class Notification(models.Model):
    ORDER = 'order'
    MESSAGE = 'message'
    REVIEW = 'review'
    VENDOR = 'vendor'
    SYSTEM = 'system'
    TYPE_CHOICES = [
        (ORDER, 'Order'), (MESSAGE, 'Message'),
        (REVIEW, 'Review'), (VENDOR, 'Vendor'), (SYSTEM, 'System'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=SYSTEM)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} - {self.title}"
