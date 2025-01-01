"""
توجيه WebSocket لتطبيق العقارات
يحدد مسارات WebSocket للتعامل مع العقارات في الوقت الفعلي
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # مسار WebSocket للعقارات - يتعامل مع كل العمليات المتعلقة بالعقارات
    re_path(r'ws/properties/$', consumers.PropertyConsumer.as_asgi()),
]
