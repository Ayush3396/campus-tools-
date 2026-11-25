"""
Django settings for campus_exchange project.

Campus Item Lending & Exchange System
CA2 Project - Django Web Application
"""

from pathlib import Path

# ------------------------------------------------------------
# BASE_DIR
# This tells Django where the root of the project is.
# Path(__file__) = location of this settings.py file
# .resolve().parent.parent = go up two levels to reach the project root
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------
# SECURITY SETTINGS
# SECRET_KEY: Used to sign cookies, sessions, tokens.
# Keep this secret in production. For development it's fine as-is.
# DEBUG: When True, Django shows detailed error pages. 
#        Always set to False in production.
# ALLOWED_HOSTS: Domains that can serve this app. 
#        Empty list is fine for local development.
# ------------------------------------------------------------
SECRET_KEY = 'django-insecure-(1hwp$gfb3$dx6969-p06-#@98m_3xfyt645+dziav3!e1uhl+'

DEBUG = True

ALLOWED_HOSTS = []


# ------------------------------------------------------------
# INSTALLED_APPS
# These are all the Django apps (built-in + our custom apps)
# that are active in this project.
#
# django.contrib.admin     → Django Admin panel
# django.contrib.auth      → Authentication system (User, login, logout)
# django.contrib.contenttypes → Generic relationships between models
# django.contrib.sessions  → Session framework (stores user sessions)
# django.contrib.messages  → Flash messages (success, error alerts)
# django.contrib.staticfiles → Serves CSS, JS, image files
#
# 'accounts'               → Our custom app for registration, login, logout
# 'marketplace'            → Our custom app for items, requests, dashboard
# ------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our custom apps
    'accounts',
    'marketplace',
]


# ------------------------------------------------------------
# MIDDLEWARE
# Middleware are functions that process every request before
# it reaches the view, and every response before it goes to the user.
#
# SecurityMiddleware     → Adds security headers
# SessionMiddleware      → Loads the user session on every request
# CommonMiddleware       → Handles URL normalization
# CsrfViewMiddleware     → Protects POST forms from cross-site attacks
# AuthenticationMiddleware → Attaches request.user to every request
# MessageMiddleware      → Enables flash messages
# XFrameOptionsMiddleware → Prevents clickjacking
# ------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ------------------------------------------------------------
# ROOT_URLCONF
# Tells Django which file contains the main URL configuration.
# It will look at campus_exchange/urls.py first.
# ------------------------------------------------------------
ROOT_URLCONF = 'campus_exchange.urls'


# ------------------------------------------------------------
# TEMPLATES
# Tells Django how to find and render HTML template files.
#
# BACKEND: Use Django's default template engine
# DIRS: We add BASE_DIR / 'templates' so Django looks in our
#       top-level 'templates/' folder (which we created)
# APP_DIRS: Also look inside each app's own 'templates/' folder
# context_processors: Automatically add useful variables to every 
#       template (request, user, messages, etc.)
# ------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # <-- Our top-level templates folder
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


# ------------------------------------------------------------
# WSGI APPLICATION
# Entry point for the web server when deploying.
# Not relevant for local development but required.
# ------------------------------------------------------------
WSGI_APPLICATION = 'campus_exchange.wsgi.application'


# ------------------------------------------------------------
# DATABASE
# We use SQLite — the simplest database.
# Django automatically creates a file called db.sqlite3 in the 
# project root. No separate database server is needed.
# ------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ------------------------------------------------------------
# PASSWORD VALIDATORS
# These rules are applied when a user sets a password.
# UserAttributeSimilarityValidator → Password must not resemble username
# MinimumLengthValidator           → Password must be at least 8 characters
# CommonPasswordValidator          → Password must not be "password123" etc.
# NumericPasswordValidator         → Password must not be all numbers
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# INTERNATIONALIZATION
# Language and timezone settings.
# TIME_ZONE is set to India's timezone.
# USE_TZ = True means Django stores all times in UTC internally
# but converts to IST when displaying.
# ------------------------------------------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# ------------------------------------------------------------
# STATIC FILES
# Static files = CSS, JavaScript, and design images.
# STATIC_URL: The URL prefix used in browser requests (e.g. /static/style.css)
# STATICFILES_DIRS: Where Django looks for static files in development.
#       We tell it to look in our top-level 'static/' folder.
# ------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']


# ------------------------------------------------------------
# MEDIA FILES
# Media files = user-uploaded content (item images).
# MEDIA_URL: URL prefix for uploaded files (e.g. /media/items/image.jpg)
# MEDIA_ROOT: Folder on disk where uploaded files are stored.
#       Django saves uploaded images here.
# ------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ------------------------------------------------------------
# AUTHENTICATION REDIRECTS
# LOGIN_URL: Where to redirect a user who tries to access a 
#       @login_required view without being logged in.
# LOGIN_REDIRECT_URL: Where to send the user after a successful login.
# LOGOUT_REDIRECT_URL: Where to send the user after logout.
# ------------------------------------------------------------
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'


# ------------------------------------------------------------
# DEFAULT AUTO FIELD
# Tells Django what type of primary key to use by default for models.
# BigAutoField = auto-incrementing integer (64-bit).
# This avoids a migration warning on newer Django versions.
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
