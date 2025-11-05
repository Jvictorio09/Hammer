from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0i&)ni%4j5)#f4y$yw7)op(d-f24b5qnp_z1ymh!=-o)d08@r-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# settings.py

ALLOWED_HOSTS = [
    'hammer-production-315f.up.railway.app',
    'localhost',
    '127.0.0.1',
    'www.hammer-services.com',
    'hammer-services.com',

]

CSRF_TRUSTED_ORIGINS = [
    'https://hammer-production-315f.up.railway.app',
    'https://www.hammer-services.com',
    'https://hammer-services.com',
    
]

# Security Settings - HTTPS Redirect
# Redirect all HTTP requests to HTTPS
# Note: Railway/nginx should handle this, but Django setting ensures it works
SECURE_SSL_REDIRECT = True  # Set to False for local development
# Only redirect in production (when DEBUG is False)
if DEBUG:
    SECURE_SSL_REDIRECT = False

# Additional security headers
SECURE_HSTS_SECONDS = 31536000  # 1 year - tells browsers to only use HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # For sitemap.xml
    'cloudinary',
    'cloudinary_storage',
    'myApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myApp.context_processors.nav_services',
                'myApp.context_processors.page_metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'myProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# MIGRATION: Dual-database configuration for SQLite → PostgreSQL migration
# After migration is complete, remove the 'sqlite' entry and keep only 'default'

import dj_database_url

# Check if DATABASE_URL is set (for PostgreSQL on Railway)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # MIGRATION: Production/PostgreSQL configuration
    # Parse DATABASE_URL and ensure SSL is required for Railway
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        ),
        # MIGRATION: Keep SQLite available for data export during migration
        'sqlite': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # MIGRATION: Development/SQLite configuration (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']          # where YOUR assets live during dev
STATIC_ROOT = BASE_DIR / 'staticfiles'            # where collectstatic puts files for prod

# Optional but recommended for Railway:
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # right after SecurityMiddleware
STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    }
}


DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
MEDIA_URL = "/media/"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# settings.py


RESEND_API_KEY   = os.getenv('RESEND_API_KEY', '')
# Use hammer-services.com for FROM address (must be verified in Resend)
RESEND_FROM      = os.getenv('RESEND_FROM', 'Hammer <noreply@hammer-services.com>')
RESEND_REPLY_TO  = os.getenv('RESEND_REPLY_TO', 'info@hammer-services.com')
RESEND_BASE_URL  = os.getenv('RESEND_BASE_URL', 'https://api.resend.com')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@hammer-services.com')

# Contact form recipient (for testing)
CONTACT_TO_EMAIL = 'info@hammer-services.com'

# Server-side sanitize allowlists (optional; templatetag will fallback if bleach unavailable)
BLEACH_ALLOWED_TAGS = [
    "p","h2","h3","strong","em","u","a","ul","ol","li","blockquote","code","pre","hr",
    "table","thead","tbody","tr","th","td","img","figure","figcaption","div","span","button"
]
BLEACH_ALLOWED_ATTRIBUTES = {
    "a": ["href","title","target","rel"],
    "img": ["src","alt","width","height","loading"],
    "*": ["class"]
}
BLEACH_ALLOWED_PROTOCOLS = ["http","https","mailto","tel"]
