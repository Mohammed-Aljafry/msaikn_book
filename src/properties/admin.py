"""
تسجيل نماذج العقارات في لوحة الإدارة
يتيح للمشرفين إدارة العقارات والطلبات والتعليقات من خلال واجهة الإدارة
"""

from django.contrib import admin
from .models import Property, PropertyRequest, PropertyImage, PropertyComment, Chat, Message

class PropertyImageInline(admin.TabularInline):
    """
    عرض صور العقار مباشرة في صفحة تحرير العقار
    """
    model = PropertyImage
    extra = 1

class PropertyCommentInline(admin.TabularInline):
    """
    عرض تعليقات العقار مباشرة في صفحة تحرير العقار
    """
    model = PropertyComment
    extra = 0
    readonly_fields = ('user', 'created_at')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    تخصيص عرض وإدارة العقارات في لوحة الإدارة
    """
    list_display = ('title', 'price', 'location', 'property_type', 'created_at')
    list_filter = ('property_type', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline, PropertyCommentInline]
    date_hierarchy = 'created_at'

@admin.register(PropertyRequest)
class PropertyRequestAdmin(admin.ModelAdmin):
    """
    تخصيص عرض وإدارة طلبات العقارات في لوحة الإدارة
    """
    list_display = ('user', 'property', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'property__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(PropertyComment)
class PropertyCommentAdmin(admin.ModelAdmin):
    """
    تخصيص عرض وإدارة التعليقات في لوحة الإدارة
    """
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'property__title', 'content')
    readonly_fields = ('created_at',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """
    تخصيص عرض وإدارة المحادثات في لوحة الإدارة
    """
    list_display = ('id', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    filter_horizontal = ('participants',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    تخصيص عرض وإدارة الرسائل في لوحة الإدارة
    """
    list_display = ('user', 'chat', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')
    readonly_fields = ('created_at',)
