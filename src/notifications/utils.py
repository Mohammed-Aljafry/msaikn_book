from django.contrib.contenttypes.models import ContentType
from .models import Notification

def create_notification(sender, recipient, notification_type, content_object, text):
    """
    إنشاء إشعار جديد
    
    المعاملات:
        sender: المستخدم الذي قام بالإجراء
        recipient: المستخدم الذي سيتلقى الإشعار
        notification_type: نوع الإشعار (message, property, follow, like, comment)
        content_object: الكائن المرتبط بالإشعار (مثل العقار أو التعليق)
        text: نص الإشعار
    """
    if sender != recipient:  # لا نريد إنشاء إشعارات للمستخدم نفسه
        content_type = ContentType.objects.get_for_model(content_object)
        
        # التحقق من عدم وجود إشعار مماثل
        existing_notification = Notification.objects.filter(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            content_type=content_type,
            object_id=content_object.id,
            is_read=False
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                content_type=content_type,
                object_id=content_object.id,
                text=text
            )
