"""
وحدات العرض للصفحة الرئيسية
يحتوي على جميع وظائف العرض المتعلقة بالصفحة الرئيسية والصفحات الثابتة
"""

from django.shortcuts import render
from properties.models import Property, PropertyRequest
from django.db.models import Q, Count
from django.core.paginator import Paginator

def home(request):
    """
    عرض الصفحة الرئيسية
    يعرض أحدث العقارات والعقارات المميزة
    """
    # الحصول على العقارات المميزة (أحدث 6 عقارات)
    featured_properties = Property.objects.all().order_by('-created_at')[:6]
    
    # الحصول على استعلام البحث
    query = request.GET.get('q')
    if query:
        properties = Property.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(property_type__icontains=query)
        ).order_by('-created_at')
    else:
        properties = Property.objects.all().order_by('-created_at')[:12]
    
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()
        print('auth')
        print(unread_notifications)
    else:
        unread_notifications = 0
        print('unauth')
    
    context = {
        'featured_properties': featured_properties,
        'properties': properties,
        'query': query,
        'unread_notifications': unread_notifications,
        'title': 'الصفحة الرئيسية'
    }
    return render(request, 'home/index.html', context)

def about(request):
    """
    عرض صفحة من نحن
    تحتوي على معلومات عن الموقع والشركة
    """
    return render(request, 'home/about.html')

def contact(request):
    """
    عرض صفحة اتصل بنا
    تحتوي على نموذج الاتصال ومعلومات التواصل
    """
    return render(request, 'home/contact.html')
