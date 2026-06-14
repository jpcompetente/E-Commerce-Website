from django.db import models
from django.conf import settings

class Conversation(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations'
    )
    store = models.ForeignKey('vendors.Store', on_delete=models.CASCADE, related_name='conversations')
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL, null=True, blank=True
    )
    subject = models.CharField(max_length=200, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['buyer', 'store', 'product']
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.buyer.email} ↔ {self.store.name}"

    @property
    def last_message(self):
        return self.messages.order_by('-sent_at').first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.email}"