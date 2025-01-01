"""
مسارات URL للصفحة الرئيسية
يحتوي على توجيهات URL الخاصة بالصفحة الرئيسية للموقع
"""

from django.urls import path
from . import views

app_name = 'home'

# قائمة المسارات
urlpatterns = [
    # الصفحة الرئيسية
    path('', views.home, name='home'),
    # صفحة من نحن
    path('about/', views.about, name='about'),
    # صفحة اتصل بنا
    path('contact/', views.contact, name='contact'),
]
