def notifications_context(request):
    """
    Globally injects the unread notifications for the logged-in user into templates.
    """
    if request.user.is_authenticated:
        unread = request.user.notifications.filter(is_read=False)
        return {
            'unread_notifications_count': unread.count(),
            'latest_notifications': unread[:5]
        }
    return {}
