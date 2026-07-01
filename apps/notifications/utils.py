from .models import Notification


def notify(recipient, title, message='', link='', notif_type='system'):
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        link=link,
        notif_type=notif_type,
    )
