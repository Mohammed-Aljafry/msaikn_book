"""
مستهلك WebSocket للعقارات
يتعامل مع كل العمليات المتعلقة بالعقارات في الوقت الفعلي
يوفر الوظائف التالية:
- إنشاء وتحديث وحذف العقارات
- البحث عن العقارات
- إدارة طلبات العقارات
- التفاعل مع العقارات (إعجاب، تعليق)
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Property, PropertyRequest, PropertyImage, PropertyComment
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PropertyConsumer(AsyncWebsocketConsumer):
    """
    مستهلك WebSocket للعقارات
    يدير اتصالات WebSocket للتفاعل مع العقارات في الوقت الفعلي
    """

    async def connect(self):
        """
        معالجة اتصال المستخدم
        يتم استدعاؤها عند فتح اتصال WebSocket جديد
        تقوم بإضافة المستخدم إلى مجموعة العقارات
        """
        await self.channel_layer.group_add(
            "properties",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        معالجة قطع اتصال المستخدم
        يتم استدعاؤها عند إغلاق اتصال WebSocket
        تقوم بإزالة المستخدم من مجموعة العقارات
        """
        await self.channel_layer.group_discard(
            "properties",
            self.channel_name
        )

    async def receive(self, text_data):
        """
        معالجة الرسائل الواردة من المستخدم
        يتم استدعاؤها عند استلام رسالة من المستخدم
        تقوم بتوجيه الرسالة إلى الدالة المناسبة حسب نوع العملية
        
        المعاملات:
            text_data (str): البيانات الواردة من المستخدم بصيغة JSON
        """
        data = json.loads(text_data)
        action = data.get('action')
        
        # عمليات العقارات
        if action == 'create_property':
            response = await self.create_property(data)
        elif action == 'update_property':
            response = await self.update_property(data)
        elif action == 'delete_property':
            response = await self.delete_property(data)
        elif action == 'get_property':
            response = await self.get_property(data)
        elif action == 'list_properties':
            response = await self.list_properties(data)
        elif action == 'search_properties':
            response = await self.search_properties(data)
            
        # عمليات الطلبات
        elif action == 'create_request':
            response = await self.create_request(data)
        elif action == 'update_request':
            response = await self.update_request(data)
        elif action == 'delete_request':
            response = await self.delete_request(data)
        elif action == 'get_request':
            response = await self.get_request(data)
            
        # التفاعلات
        elif action == 'like_property':
            response = await self.toggle_property_like(data)
        elif action == 'add_comment':
            response = await self.add_comment(data)
        elif action == 'like_comment':
            response = await self.toggle_comment_like(data)
            
        # إرسال الرد للمستخدم
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def create_property(self, data):
        """
        إنشاء عقار جديد
        
        المعاملات:
            data (dict): بيانات العقار المراد إنشاؤه
        
        العائد:
            dict: رسالة نجاح أو فشل العملية
        """
        try:
            property_data = data.get('property')
            property = Property.objects.create(
                owner=self.scope["user"],
                **property_data
            )
            return {
                'status': 'success',
                'message': 'تم إنشاء العقار بنجاح',
                'property_id': property.id
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @database_sync_to_async
    def update_property(self, data):
        """
        تحديث بيانات عقار
        
        المعاملات:
            data (dict): بيانات العقار المراد تحديثها
        
        العائد:
            dict: رسالة نجاح أو فشل العملية
        """
        try:
            property_id = data.get('property_id')
            property_data = data.get('property')
            property = Property.objects.get(id=property_id, owner=self.scope["user"])
            for key, value in property_data.items():
                setattr(property, key, value)
            property.save()
            return {
                'status': 'success',
                'message': 'تم تحديث العقار بنجاح'
            }
        except Property.DoesNotExist:
            return {
                'status': 'error',
                'message': 'العقار غير موجود'
            }

    @database_sync_to_async
    def delete_property(self, data):
        """
        حذف عقار
        
        المعاملات:
            data (dict): بيانات العقار المراد حذفه
        
        العائد:
            dict: رسالة نجاح أو فشل العملية
        """
        try:
            property_id = data.get('property_id')
            property = Property.objects.get(id=property_id, owner=self.scope["user"])
            property.delete()
            return {
                'status': 'success',
                'message': 'تم حذف العقار بنجاح'
            }
        except Property.DoesNotExist:
            return {
                'status': 'error',
                'message': 'العقار غير موجود'
            }

    @database_sync_to_async
    def search_properties(self, data):
        """
        البحث في العقارات
        
        المعاملات:
            data (dict): معايير البحث
                - query: نص البحث
                - type: نوع العقار
                - min_price: السعر الأدنى
                - max_price: السعر الأعلى
                - location: الموقع
        
        العائد:
            dict: نتائج البحث
        """
        try:
            query = data.get('query', '')
            property_type = data.get('type')
            min_price = data.get('min_price')
            max_price = data.get('max_price')
            location = data.get('location')

            properties = Property.objects.all()

            if query:
                properties = properties.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            if property_type:
                properties = properties.filter(property_type=property_type)
            if min_price:
                properties = properties.filter(price__gte=min_price)
            if max_price:
                properties = properties.filter(price__lte=max_price)
            if location:
                properties = properties.filter(location__icontains=location)

            return {
                'status': 'success',
                'properties': [self.property_to_dict(p) for p in properties]
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def property_to_dict(self, property):
        """
        تحويل نموذج العقار إلى قاموس
        
        المعاملات:
            property (Property): نموذج العقار
        
        العائد:
            dict: بيانات العقار بصيغة قاموس
        """
        return {
            'id': property.id,
            'title': property.title,
            'description': property.description,
            'price': str(property.price),
            'location': property.location,
            'property_type': property.property_type,
            'listing_type': property.listing_type,
            'created_at': property.created_at.isoformat(),
            'owner': property.owner.username
        }
