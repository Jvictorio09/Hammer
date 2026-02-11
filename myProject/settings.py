from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
# Try both the project root and parent directory
env_path1 = BASE_DIR / '.env'
env_path2 = BASE_DIR.parent / '.env'

# Debug: Show where we're looking for .env file
print(f"🔍 Looking for .env file at: {env_path1}")
print(f"🔍 Also checking: {env_path2}")

loaded1 = load_dotenv(env_path1)
loaded2 = load_dotenv(env_path2)  # Also check parent directory

if loaded1:
    print(f"✅ Loaded .env from: {env_path1}")
elif loaded2:
    print(f"✅ Loaded .env from: {env_path2}")
else:
    print(f"⚠️  WARNING: .env file not found at {env_path1} or {env_path2}")
    print(f"   Please create .env file with DATABASE_URL in: {env_path1}")


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
    'django.contrib.sitemaps',
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

# Database configuration
# Always use DATABASE_URL if available (PostgreSQL), fallback to SQLite only if not set
# DATABASE_URL is loaded directly from .env file using dotenv (already loaded at top of file)
import dj_database_url
import os

# Load DATABASE_URL directly from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# Debug: Show if DATABASE_URL is loaded (mask password for security)
if DATABASE_URL:
    # Mask the password in the URL for logging
    try:
        masked_url = DATABASE_URL.split('@')[0].split(':')[0] + ':***@' + '@'.join(DATABASE_URL.split('@')[1:]) if '@' in DATABASE_URL else DATABASE_URL
        print(f"✅ DATABASE_URL loaded from .env: {masked_url}")
    except:
        print(f"✅ DATABASE_URL loaded from .env")
else:
    print("⚠️  WARNING: DATABASE_URL not found in .env file, using SQLite fallback")

if DATABASE_URL:
    # Parse DATABASE_URL and configure for Railway PostgreSQL with SSL
    # Railway requires SSL connections - configure explicitly
    db_config = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=0,  # Disable connection pooling for migrations
    )
    
    # Ensure SSL is required for Railway database
    if 'OPTIONS' not in db_config:
        db_config['OPTIONS'] = {}
    
    # Set SSL mode - Railway databases require SSL
    db_config['OPTIONS']['sslmode'] = 'require'
    
    DATABASES = {
        "default": db_config
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
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

# Google reCAPTCHA settings (v3)
# Get your keys from: https://www.google.com/recaptcha/admin
# IMPORTANT: Make sure to register for reCAPTCHA v3, not v2
# 
# HARDCODED KEYS - Paste your reCAPTCHA v3 keys here:
# 
# From Google reCAPTCHA Admin Console:
# - SITE KEY (also called "Key") goes in RECAPTCHA_SITE_KEY
# - SECRET KEY goes in RECAPTCHA_SECRET_KEY
#
RECAPTCHA_SITE_KEY = '6LenShAsAAAAADoaC3f0y1xp4eQVJpc_G1NrNOxA'  # ← Your Site Key (Key ID from Google Console)
RECAPTCHA_SECRET_KEY = '6LenShAsAAAAADXvezHZ96Wvd3q4fEZXBlKNsUt5'  # ← Your Secret Key

# Fallback to environment variables ONLY if hardcoded keys above are empty
# (Do NOT override if keys are already set above)
if not RECAPTCHA_SITE_KEY:
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
if not RECAPTCHA_SECRET_KEY:
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')

# Debug: Print if keys are loaded
if not RECAPTCHA_SITE_KEY:
    print("⚠️  WARNING: RECAPTCHA_SITE_KEY is not set. Check settings.py or environment variables.")
else:
    print(f"✅ RECAPTCHA_SITE_KEY loaded: {RECAPTCHA_SITE_KEY[:10]}...")
if not RECAPTCHA_SECRET_KEY:
    print("⚠️  WARNING: RECAPTCHA_SECRET_KEY is not set. Check settings.py or environment variables.")
else:
    print(f"✅ RECAPTCHA_SECRET_KEY loaded: {RECAPTCHA_SECRET_KEY[:10]}...")

RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

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
