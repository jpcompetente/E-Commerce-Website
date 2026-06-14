from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'store', 'is_resolved', 'created_at']
    list_filter = ['is_resolved']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'is_read', 'sent_at']
    list_filter = ['is_read']