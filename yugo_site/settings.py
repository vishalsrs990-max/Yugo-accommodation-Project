from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------
SECRET_KEY = 'django-insecure-change-this-for-yugo-demo'

DEBUG = True

# Allow Cloud9 and local browsers
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.vfs.cloud9.us-east-1.amazonaws.com',
]

# -----------------------------------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'accommodation.apps.AccommodationConfig',

    # Needed for S3Boto3Storage
    'storages',
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

ROOT_URLCONF = 'yugo_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Global templates folder
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'yugo_site.wsgi.application'

# -----------------------------------------------------------------------------
# DATABASE
# -----------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------------------------------------------------------------
# PASSWORD VALIDATION
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# INTERNATIONALIZATION
# -----------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# STATIC FILES
# -----------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Optional extra static dir (create BASE_DIR / 'static' or remove this)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# -----------------------------------------------------------------------------
# DEFAULT MEDIA (overridden by S3 block when USE_S3=True)
# -----------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------------------------------------------------------------
# S3 SETTINGS FOR YOUR YUGO PROJECT
# -----------------------------------------------------------------------------

# Your actual bucket name + region
YUGO_S3_BUCKET_NAME = "yugo-accommodation-buckets"
YUGO_AWS_REGION = "us-east-1"

# Base URL for public objects (still useful for some helpers)
YUGO_S3_BASE_URL = (
    f"https://{YUGO_S3_BUCKET_NAME}.s3.{YUGO_AWS_REGION}.amazonaws.com"
)

# Name used by django-storages
AWS_STORAGE_BUCKET_NAME = YUGO_S3_BUCKET_NAME

# Use S3 for media files
USE_S3 = True  # you can switch to False for local dev if needed

if USE_S3:
    AWS_S3_REGION_NAME = YUGO_AWS_REGION
    AWS_S3_CUSTOM_DOMAIN = (
        f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    )
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    # All FileField/ImageField will go to S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # Media URL points to S3
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -----------------------------------------------------------------------------
# LAMBDA + SNS BOOKING EMAIL
# -----------------------------------------------------------------------------
BOOKING_LAMBDA_NAME = 'yugo-booking'
AWS_REGION_NAME = 'us-east-1'

# -----------------------------------------------------------------------------
# DEFAULT AUTO FIELD
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = 'login'                # where @login_required sends anonymous users
LOGIN_REDIRECT_URL = 'home'        # after successful login
LOGOUT_REDIRECT_URL = 'login'       # after logout
