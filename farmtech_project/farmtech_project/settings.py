import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '*.replit.dev', '*.worf.replit.dev', '*.repl.co', '27fe9ebd-75c0-4f9f-af15-ad8c24c2843c-00-1dazfnvwimpmc.worf.replit.dev']

CSRF_TRUSTED_ORIGINS = ['https://*.replit.dev', 'https://*.worf.replit.dev', 'https://*.repl.co', 'https://27fe9ebd-75c0-4f9f-af15-ad8c24c2843c-00-1dazfnvwimpmc.worf.replit.dev']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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

ROOT_URLCONF = 'farmtech_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'farmtech_project.wsgi.application'

# Database configuration
# Check if we're running on Replit (environment-based detection)
import sys
IS_REPLIT = 'REPLIT_DB_URL' in os.environ

# Use SQLite for Replit environment, MySQL for local development with XAMPP
if IS_REPLIT:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # MySQL configuration for XAMPP
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'reve_platform_db',  # Create this database in phpMyAdmin
            'USER': 'root',              # Default XAMPP MySQL username
            'PASSWORD': '',              # Default XAMPP MySQL password is empty
            'HOST': '127.0.0.1',         # Typically localhost/127.0.0.1 for XAMPP
            'PORT': '3306',              # Default MySQL port
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            }
        }
    }

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"

# Add this line
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# If you also want to serve static files during development:
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Login URLs
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
# Legacy OpenAI reference - will be replaced in future updates
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
