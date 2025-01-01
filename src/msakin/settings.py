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
            "hosts": [config('REDIS_URL', default='redis://127.0.0.1:6379')],
        },
    }
}

# إعدادات قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('PGDATABASE', default='railway'),
        'USER': config('PGUSER', default='postgres'),
        'PASSWORD': config('PGPASSWORD'),
        'HOST': config('PGHOST', default='localhost'),
        'PORT': config('PGPORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

if config('DATABASE_URL', default=None):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )

# إعدادات التخزين المؤقت
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# إعدادات الجلسات
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 14 days

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
USE_L10N = True
USE_TZ = True               # دعم المناطق الزمنية

# إعدادات الأمان
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# إعدادات CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://msakin-book.up.railway.app',
]
CSRF_TRUSTED_ORIGINS = [
    'https://msakin-book.up.railway.app',
]

# إعدادات الملفات الثابتة
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# إعدادات الوسائط
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# إعدادات Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# إعدادات المصادقة
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# إعدادات البريد الإلكتروني
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@msakin-book.up.railway.app'

# إعدادات الملفات المرفوعة
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# إعدادات المستخدم الافتراضي
AUTH_USER_MODEL = 'auth.User'
