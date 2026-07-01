def notifications_context(request):
    if request.user.is_authenticated:
        qs = request.user.notifications.all()
        return {
            'unread_notif_count': qs.filter(is_read=False).count(),
            'recent_notifications': qs[:5],
        }
    return {'unread_notif_count': 0, 'recent_notifications': []}
