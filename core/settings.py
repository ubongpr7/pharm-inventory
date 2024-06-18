
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-pvc)e7cia$y25l0lc^b@#j+5c628x8+b(^eirvpgk3$z6^t8wh'

DEBUG = True

ALLOWED_HOSTS = []


# Application definition
DJ_DEFAULT_INSTALLED_APPS=[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS=[
    "widget_tweaks",
    "bootstrap5",
    "cities_light",
    'django_extensions',
    "django_htmx",
    
]
CORE_APPS = [
    
    'mainapps.accounts',
    'mainapps.common',
    'mainapps.company',
    'mainapps.content_type_linking_models',
    'mainapps.inventory',
    'mainapps.management',
    'mainapps.orders',
    'mainapps.permit',
    'mainapps.stock',
]
INSTALLED_APPS=[
]
INSTALLED_APPS.extend(DJ_DEFAULT_INSTALLED_APPS) 
INSTALLED_APPS.extend(THIRD_PARTY_APPS) 
INSTALLED_APPS.extend(CORE_APPS) 


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
    # 'middleware.logging_middleware.LoggingMiddleWare',
    'middleware.ip_address_middleware.IPBlackListMiddleware',
]

BANNED_IPS=['127.0.0.']

ROOT_URLCONF = 'core.urls'
AUTH_USER_MODEL = 'accounts.User' 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/"templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# AUTHENTICATION_BACKENDS = (
#     'mainapps.accounts.backends.UserBackend',
#     'django.contrib.auth.backends.ModelBackend',
#     'mainapps.management.backends.StaffUserBackend',
# )

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
# CITIES_LIGHT_TRANSLATION_LANGUAGES = ['fr', 'en']
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en']

# CITIES_LIGHT_INCLUDE_COUNTRIES = ['FR']
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]
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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOGIN_URL='/accounts/signin'
LOGIN_REDIRECT_URL='/accounts/signin/?next={url}'
DEFAULT_REDIEECT_URL='/'
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  

STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]

MEDIA_URL = '/media/'
MEDIAFILES_DIRS=[os.path.join(BASE_DIR,'media')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465  
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = "ubongpr7@gmail.com"
EMAIL_HOST_PASSWORD = "nmcmiwlgwdrwesef"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
    