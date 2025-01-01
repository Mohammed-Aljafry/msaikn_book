"""
نماذج البيانات الخاصة بالعقارات
يحتوي على جميع النماذج المتعلقة بالعقارات وخصائصها وتفاعلات المستخدمين معها
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Property(models.Model):
    """
    نموذج العقار الأساسي
    يحتوي على جميع معلومات العقار الأساسية
    """
    # خيارات نوع العقار
    PROPERTY_TYPE_CHOICES = [
        ('apartment', _('شقة')),
        ('house', _('منزل')),
        ('villa', _('فيلا')),
        ('land', _('أرض')),
        ('commercial', _('تجاري')),
    ]

    # خيارات نوع العرض
    LISTING_TYPE_CHOICES = [
        ('sale', _('للبيع')),
        ('rent', _('للإيجار')),
    ]

    # معلومات العقار الأساسية
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties', verbose_name=_('المالك'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(verbose_name=_('الوصف'))
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, verbose_name=_('نوع العقار'))
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, verbose_name=_('نوع العرض'))
    
    # التفاصيل المالية والمساحة
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('السعر'))
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('المساحة'))
    
    # مواصفات العقار
    bedrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('عدد غرف النوم'))
    bathrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('عدد الحمامات'))
    
    # الموقع
    location = models.CharField(max_length=200, verbose_name=_('الموقع'))
    address = models.TextField(verbose_name=_('العنوان التفصيلي'))
    
    # معلومات النظام
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    is_available = models.BooleanField(default=True, verbose_name=_('متاح'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد المشاهدات'))
    
    # العلاقات
    liked_by = models.ManyToManyField(User, related_name='liked_properties', blank=True, verbose_name=_('المعجبين'))

    class Meta:
        verbose_name = _('عقار')
        verbose_name_plural = _('عقارات')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    """
    نموذج صور العقار
    يحتفظ بصور العقار مع إمكانية تحديد الصورة الرئيسية
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images', verbose_name=_('العقار'))
    image = models.ImageField(upload_to='property_images/', verbose_name=_('الصورة'))
    is_primary = models.BooleanField(default=False, verbose_name=_('صورة رئيسية'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإضافة'))

    class Meta:
        verbose_name = _('صورة العقار')
        verbose_name_plural = _('صور العقار')
        ordering = ['-is_primary', '-created_at']

class PropertyRequest(models.Model):
    """
    نموذج طلب العقار
    يحتفظ بطلبات المستخدمين للعقارات
    """
    PROPERTY_TYPES = [
        ('apartment', _('شقة')),
        ('villa', _('فيلا')),
        ('land', _('أرض')),
        ('commercial', _('تجاري')),
    ]
    
    LISTING_TYPES = [
        ('sale', _('للبيع')),
        ('rent', _('للإيجار')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_requests', verbose_name=_('المستخدم'))
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='requests', null=True, verbose_name=_('العقار'))
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, verbose_name=_('نوع العقار'))
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, verbose_name=_('نوع العرض'))
    preferred_location = models.CharField(max_length=255, verbose_name=_('الموقع المفضل'))
    max_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('السعر الأقصى'))
    min_area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('المساحة الأدنى'))
    bedrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('عدد غرف النوم'))
    bathrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('عدد الحمامات'))
    description = models.TextField(verbose_name=_('الوصف'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    is_read = models.BooleanField(default=False, verbose_name=_('تم القراءة'))

    class Meta:
        verbose_name = _('طلب العقار')
        verbose_name_plural = _('طلبات العقار')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s request for {self.property_type}"

class PropertyLike(models.Model):
    """
    نموذج إعجاب العقار
    يحتفظ بإعجابات المستخدمين للعقارات
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_likes', verbose_name=_('المستخدم'))
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='likes', verbose_name=_('العقار'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        unique_together = ('user', 'property')
        verbose_name = _('إعجاب العقار')
        verbose_name_plural = _('إعجابات العقار')

class PropertyComment(models.Model):
    """
    نموذج تعليق العقار
    يحتفظ بتعليقات المستخدمين على العقارات
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_comments', verbose_name=_('المستخدم'))
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments', verbose_name=_('العقار'))
    content = models.TextField(verbose_name=_('المحتوى'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    liked_by = models.ManyToManyField(User, related_name='liked_comments', through='CommentLike', verbose_name=_('المعجبين'))
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name=_('الرد'))

    class Meta:
        verbose_name = _('تعليق العقار')
        verbose_name_plural = _('تعليقات العقار')
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.property.title}'

class CommentLike(models.Model):
    """
    نموذج إعجاب التعليق
    يحتفظ بإعجابات المستخدمين للتعليقات
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes', verbose_name=_('المستخدم'))
    comment = models.ForeignKey(PropertyComment, on_delete=models.CASCADE, related_name='likes', verbose_name=_('التعليق'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        unique_together = ('user', 'comment')
        verbose_name = _('إعجاب التعليق')
        verbose_name_plural = _('إعجابات التعليقات')

class UserFollow(models.Model):
    """
    نموذج متابعة المستخدم
    يحتفظ بمتابعة المستخدمين لبعضهم البعض
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name=_('المتابع'))
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', verbose_name=_('المتابع'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = _('متابعة المستخدم')
        verbose_name_plural = _('متابعات المستخدمين')

class Chat(models.Model):
    """
    نموذج المحادثة
    يحتفظ بمحادثات المستخدمين
    """
    participants = models.ManyToManyField(User, related_name='chats', verbose_name=_('المشاركون'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('محادثة')
        verbose_name_plural = _('محادثات')
        ordering = ['-updated_at']

class Message(models.Model):
    """
    نموذج الرسالة
    يحتفظ برسائل المستخدمين
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name=_('المحادثة'))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_messages', verbose_name=_('المرسل'))
    content = models.TextField(verbose_name=_('المحتوى'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    is_read = models.BooleanField(default=False, verbose_name=_('تم القراءة'))

    class Meta:
        verbose_name = _('رسالة')
        verbose_name_plural = _('رسائل')
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} in {self.chat}"
