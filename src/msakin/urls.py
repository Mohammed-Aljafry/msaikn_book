"""
مسارات URL الرئيسية للمشروع
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# دالة بسيطة للتحقق من الصحة
def healthcheck(request):
    return HttpResponse("OK")

urlpatterns = [
    # مسار فحص الصحة
    path('healthcheck/', healthcheck, name='healthcheck'),
    
    # مسارات الإدارة
    path('admin/', admin.site.urls),
    
    # مسارات التطبيقات
    path('', include('home.urls')),
    path('properties/', include('properties.urls')),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
