"""
خدمات WebSocket للعقارات
يوفر وظائف مساعدة للتعامل مع WebSocket والإشعارات في الوقت الفعلي
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_update(post_id):
    """
    إرسال إشعار تحديث للمستخدمين المتصلين
    
    المعاملات:
        post_id (int): معرف العقار المحدث
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"post_{post_id}",
        {
            "type": "update_event",
            "data": "تم تحديث العقار"
        }
    )