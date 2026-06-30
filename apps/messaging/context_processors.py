from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            conversation__buyer=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        if request.user.is_vendor and hasattr(request.user, 'store'):
            count += Message.objects.filter(
                conversation__store=request.user.store,
                is_read=False
            ).exclude(sender=request.user).count()

        return {'unread_message_count': count}
    return {'unread_message_count': 0}
