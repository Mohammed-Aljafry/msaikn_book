from .models import Notification

def notifications_processor(request):
    """
    إضافة عدد الإشعارات غير المقروءة إلى سياق جميع القوالب
    """
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
        
        return {
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
