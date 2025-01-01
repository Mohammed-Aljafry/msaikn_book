"""
نماذج إدخال البيانات للعقارات
يحتوي على جميع النماذج المستخدمة في صفحات إدخال وتعديل بيانات العقارات
"""

from django import forms
from .models import Property, PropertyRequest, PropertyImage
from django.utils.translation import gettext_lazy as _

class PropertyForm(forms.ModelForm):
    """
    نموذج إضافة وتعديل العقار
    يستخدم لإنشاء عقار جديد أو تعديل عقار موجود
    """
    images = forms.ImageField(
        required=False,
        label='صور العقار',
        help_text='اختر صورة للعقار. يمكنك إضافة المزيد من الصور لاحقاً.',
        error_messages={
            'invalid_image': 'الملف المختار ليس صورة صالحة.',
        }
    )
    
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'listing_type', 'price', 
                 'area', 'bedrooms', 'bathrooms', 'location', 'address']
        labels = {
            'title': _('عنوان العقار'),
            'description': _('وصف العقار'),
            'property_type': _('نوع العقار'),
            'listing_type': _('نوع العرض'),
            'price': _('السعر'),
            'area': _('المساحة'),
            'bedrooms': _('عدد غرف النوم'),
            'bathrooms': _('عدد الحمامات'),
            'location': _('الموقع'),
            'address': _('العنوان التفصيلي'),
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

class PropertyRequestForm(forms.ModelForm):
    """
    نموذج طلب عقار
    يستخدم عندما يريد المستخدم البحث عن عقار بمواصفات محددة
    """
    class Meta:
        model = PropertyRequest
        fields = ['property_type', 'listing_type', 'preferred_location', 
                 'max_price', 'min_area', 'bedrooms', 'bathrooms', 'description']
        labels = {
            'property_type': _('نوع العقار'),
            'listing_type': _('نوع العرض'),
            'preferred_location': _('الموقع المفضل'),
            'max_price': _('السعر الأقصى'),
            'min_area': _('المساحة الأدنى'),
            'bedrooms': _('عدد غرف النوم'),
            'bathrooms': _('عدد الحمامات'),
            'description': _('وصف إضافي'),
        }
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': _('اكتب وصفاً تفصيلياً لمتطلباتك...')
            }),
            'property_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'listing_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'preferred_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل الموقع المفضل')
            }),
            'max_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل السعر الأقصى')
            }),
            'min_area': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل المساحة الأدنى')
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('عدد غرف النوم')
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('عدد الحمامات')
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property_type'].choices = [('', _('اختر نوع العقار'))] + list(self.fields['property_type'].choices)[1:]
        self.fields['listing_type'].choices = [('', _('اختر نوع العرض'))] + list(self.fields['listing_type'].choices)[1:]
