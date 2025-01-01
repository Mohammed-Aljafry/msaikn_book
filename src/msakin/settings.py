"""
Django settings for msakin project.
إعدادات مشروع مساكن - نظام إدارة العقارات
"""

from pathlib import Path
import os
from decouple import config
import dj_database_url

# إعداد المسار الأساسي للمشروع
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# مفتاح الأمان - يجب تغييره في الإنتاج وحفظه بشكل آمن
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key')

# وضع التطوير - يجب إيقافه في الإنتاج
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# المواقع المسموح لها بالوصول للتطبيق
ALLOWED_HOSTS = ['*', '.railway.app', 'msakin-book.up.railway.app']  # سيتم تحديثه لاحقاً مع اسم موقعك

# تعريف التطبيقات المثبتة
# Application definition
INSTALLED_APPS = [
    'daphne',  # لدعم ASGI والـ WebSocket
    'django.contrib.admin',  # لوحة الإدارة
    'django.contrib.auth',   # نظام المصادقة
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',         # لتنسيق النماذج
    'crispy_bootstrap5',    # نمط بوتستراب 5
    'chat',                 # تطبيق المحادثات
    'home',                 # الصفحة الرئيسية
    'properties',          # تطبيق العقارات
    'accounts',            # تطبيق الحسابات
    'notifications',       # نظام الإشعارات
    'channels',           # لدعم WebSocket
    'corsheaders',         # إعدادات CORS
    'whitenoise',          # إعدادات Whitenoise
]

# الوسطاء (Middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',    # أمان
    'whitenoise.middleware.WhiteNoiseMiddleware',       # إعدادات Whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',  # إدارة الجلسات
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',       # حماية CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # المصادقة
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # حماية Clickjacking
    'corsheaders.middleware.CorsMiddleware',          # إعدادات CORS
    'django.middleware.common.CommonMiddleware',      # إعدادات CORS
]

# إعدادات توجيه URL الرئيسي
ROOT_URLCONF = 'msakin.urls'

# إعدادات القوالب
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # مجلد القوالب
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'properties.context_processors.unread_requests',  # عداد الطلبات غير المقروءة
            ],
        },
    },
]

# إعدادات WSGI و ASGI
WSGI_APPLICATION = 'msakin.wsgi.application'
ASGI_APPLICATION = 'msakin.asgi.application'

# إعدادات Channel Layers للمحادثات المباشرة
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    }
}

# إعدادات قاعدة البيانات
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('PGDATABASE'),
#         'USER': config('PGUSER'),
#         'PASSWORD': config('PGPASSWORD'),
#         'HOST': config('PGHOST'),
#         'PORT': config('PGPORT', default='5432'),
#         'OPTIONS': {
#             'sslmode': 'require',
#         }
#     }
# }



POSTGRES_LOCALLY=False
if POSTGRES_LOCALLY:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('PGDATABASE'),
            'USER': config('PGUSER'),
            'PASSWORD': config('PGPASSWORD'),
            'HOST': config('PGHOST'),
            'PORT': config('PGPORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'require',
            }
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(default=config('DATABASE_URL'))
    }
# إعدادات التخزين المؤقت
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# إعدادات الجلسات
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# التحقق من قوة كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# إعدادات اللغة والتوقيت
LANGUAGE_CODE = 'ar'          # اللغة العربية
TIME_ZONE = 'Asia/Riyadh'     # توقيت الرياض
USE_I18N = True              # دعم الترجمة
USE_TZ = True               # دعم المناطق الزمنية

# إعدادات الملفات الثابتة
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # مجلد الملفات الثابتة المجمعة
STATICFILES_DIRS = [
    BASE_DIR / 'static',    # مجلد الملفات الثابتة للتطوير
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# إعدادات ملفات الوسائط
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # مجلد الوسائط المرفوعة

# إعدادات Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# إعدادات الأمان
SECURE_SSL_REDIRECT = True          # إجبار HTTPS
SESSION_COOKIE_SECURE = True        # تأمين كوكيز الجلسة
CSRF_COOKIE_SECURE = True          # تأمين كوكيز CSRF
CSRF_TRUSTED_ORIGINS = [
    # 'https://*.railway.app',
    'https://msakin-book.up.railway.app'
]
SECURE_BROWSER_XSS_FILTER = True   # حماية XSS
SECURE_CONTENT_TYPE_NOSNIFF = True # منع تخمين نوع المحتوى
X_FRAME_OPTIONS = 'DENY'           # منع التضمين في إطارات
SECURE_HSTS_SECONDS = 31536000    # مدة HSTS (سنة)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # تطبيق HSTS على النطاقات الفرعية
SECURE_HSTS_PRELOAD = True        # السماح بالتحميل المسبق

# إعدادات CORS
CORS_ORIGIN_ALLOW_ALL = True  # في بيئة التطوير فقط
CORS_ALLOW_CREDENTIALS = True

# نوع المفتاح الرئيسي الافتراضي
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# روابط تسجيل الدخول
LOGIN_URL = 'login'  # صفحة تسجيل الدخول
LOGIN_REDIRECT_URL = 'home:home'  # صفحة إعادة التوجيه بعد الدخول
# LOGOUT_REDIRECT_URL = 'home:home'  # صفحة إعادة التوجيه بعد الخروج
