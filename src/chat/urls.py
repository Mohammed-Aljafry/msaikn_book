"""
مسارات URL لتطبيق المحادثات
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversations_list, name='conversation_list'),
    path('<int:user_id>/', views.chat_room, name='chat_room'),
]
