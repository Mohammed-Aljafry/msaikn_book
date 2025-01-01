"""
اختبارات الوحدة للصفحة الرئيسية
يحتوي على اختبارات للتأكد من صحة عمل وظائف الصفحة الرئيسية
"""

from django.test import TestCase

class HomeTests(TestCase):
    """
    اختبارات الصفحة الرئيسية
    """
    def test_home_page(self):
        """
        اختبار عرض الصفحة الرئيسية
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
