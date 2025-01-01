"""
مسارات URL الرئيسية للمشروع
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # مسارات الإدارة
    path('admin/', admin.site.urls),
    
    # مسارات التطبيقات
    path('', include('home.urls')),
    path('properties/', include('properties.urls')),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
