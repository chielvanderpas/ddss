<<<<<<< HEAD
"""
Django settings for ddss project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-57e4oxt_*ci_scew=gm2&#^=n()s1z)bvtvjirep*7tt9juu8_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
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

ROOT_URLCONF = 'ddss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['app/templates'],
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

WSGI_APPLICATION = 'ddss.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

LOGIN_URL = '/app/login'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/document/'

GraphDB_sparql_endpoint = 'http://localhost:7200/repositories/'
GraphDB_sparql_endpoint_statements = '/statements'
Media_root_rel = 'documents'
MEDIA_ROOT_REL = 'documents'

GraphDB_Repository_ID = 'test_repo'
AIM_default_namespace = 'https://github.com/chielvanderpas/aims/'
Media_root_location = 'C:/Users/chiel/Desktop/django_ddss/ddss/'
AIM_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/aims/'
ORGANIZATION_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/oms#'
CURRENT_ORG = 'https://github.com/chielvanderpas/oms#fictional_test_org'

SPARQL_ENDPOINT_1 = str(GraphDB_sparql_endpoint+GraphDB_Repository_ID)
SPARQL_ENDPOINT_2 = str(GraphDB_sparql_endpoint+GraphDB_Repository_ID+GraphDB_sparql_endpoint_statements)
MEDIA_ROOT = str(Media_root_location+Media_root_rel)

# SPARQL_ENDPOINT_1 = 'http://localhost:7200/repositories/test_repo'
# SPARQL_ENDPOINT_2 = 'http://localhost:7200/repositories/test_repo/statements'
# AIM_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/aims/'
# ORGANIZATION_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/oms#'
# CURRENT_ORG = 'https://github.com/chielvanderpas/oms#fictional_test_org'
# MEDIA_ROOT = 'C:/Users/chiel/Desktop/django_ddss/ddss/documents'
# MEDIA_ROOT_REL = 'documents'

=======
"""
Django settings for ddss project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-57e4oxt_*ci_scew=gm2&#^=n()s1z)bvtvjirep*7tt9juu8_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
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

ROOT_URLCONF = 'ddss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['app/templates'],
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

WSGI_APPLICATION = 'ddss.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

LOGIN_URL = '/app/login'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/document/'

GraphDB_sparql_endpoint = 'http://localhost:7200/repositories/'
GraphDB_sparql_endpoint_statements = '/statements'
Media_root_rel = 'documents'
MEDIA_ROOT_REL = 'documents'

GraphDB_Repository_ID = 'test_repo'
Media_root_location = 'C:/Users/chiel/Desktop/django_ddss/ddss/'
AIM_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/aims/'
ORGANIZATION_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/oms#'
CURRENT_ORG = 'https://github.com/chielvanderpas/oms#fictional_test_org'

SPARQL_ENDPOINT_1 = str(GraphDB_sparql_endpoint+GraphDB_Repository_ID)
SPARQL_ENDPOINT_2 = str(GraphDB_sparql_endpoint+GraphDB_Repository_ID+GraphDB_sparql_endpoint_statements)
MEDIA_ROOT = str(Media_root_location+Media_root_rel)
