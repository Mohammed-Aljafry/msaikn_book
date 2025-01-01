"""
مسارات URL لتطبيق العقارات
يحتوي على جميع مسارات URL المتعلقة بالعقارات وإدارتها
"""

from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # صفحات عرض العقارات
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('search/', views.property_search, name='property_search'),
    
    # إدارة العقارات
    path('add/', views.create_property, name='property_create'),
    path('<int:pk>/edit/', views.edit_property, name='property_update'),
    path('<int:pk>/delete/', views.delete_property, name='property_delete'),
    
    # التفاعل مع العقارات
    path('<int:pk>/like/', views.like_property, name='property_like'),
    path('<int:pk>/comment/', views.add_comment, name='property_comment'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    # طلبات العقارات
    path('requests/', views.my_requests, name='request_list'),
    path('requests/add/', views.create_request, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/edit/', views.edit_request, name='request_update'),
    path('requests/<int:pk>/delete/', views.delete_request, name='request_delete'),
]
