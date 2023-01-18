"""
Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from firebase_admin import initialize_app
from socket import gethostname, gethostbyname
from glob import glob

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# add gdal path
# if len(glob('/usr/lib/libgdal.so.*')):
#     GDAL_LIBRARY_PATH=glob('/usr/lib/libgdal.so.*')[0]
#     GEOS_LIBRARY_PATH=glob('/usr/lib/libgeos_c.so.*')[0]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-^pxr2pc@d81=s1*hh9t_pcs4^a-pazd_+@lv40nscf7-oh$&4w'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-^pxr2pc@d81=s1*hh9t_pcs4^a-pazd_+@lv40nscf7-oh$&4w')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
    '45.76.55.51',
    'chinghsien.com'
]
ALLOWED_HOSTS.extend(
    filter(
        None,
        os.environ.get('ALLOWED_HOSTS', '').split(',')
    )
)
if os.environ.get('AWS_EXECUTION_ENV'):
    ALLOWED_HOSTS.append(gethostbyname(gethostname()))

ADMINS = (
    ('user0', '0000000000'),
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework.authtoken',
    'modelCore',
    'user',
    'taxiApi',
    'backboard',
    'web',
    'fcmNotify',
    'fcm_django',
    'task',
]

#Get the absolute path of the settings.py file's directory
PWD = os.path.dirname(os.path.realpath(__file__ )) 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PWD, "flutterjava-firebase.json")

FIREBASE_APP = initialize_app()

#Get the absolute path of the settings.py file's directory
# PWD = os.path.dirname(os.path.realpath(__file__ )) 
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PWD, "flutterjava-firebase.json")

FCM_DJANGO_SETTINGS = {
     # default: _('FCM Django')
    "APP_VERBOSE_NAME": "FCM Django",
     # true if you want to have only one active device per registered user at a time
     # default: False
    "ONE_DEVICE_PER_USER": False,
     # devices to which notifications cannot be sent,
     # are deleted upon receiving error response from FCM
     # default: False
    "DELETE_INACTIVE_DEVICES": False,
    # Transform create of an existing Device (based on registration id) into
                # an update. See the section
    # "Update of device with duplicate registration ID" for more details.
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'djangogeo',
#         'USER': 'django_geo',
#         'PASSWORD': "django_geo",
#         'HOST' : 'localhost',
#         'PORT' : '5432',
#     },
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME','mydatabase'),
        'USER': os.environ.get('DB_USER','mydatabaseuser'),
        'PASSWORD': os.environ.get('DB_PASS','mypassword'),
        'HOST': os.environ.get('DB_HOST','localhost'),
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Base url to serve media files
MEDIA_URL = '/media/'

# Path where media is stored
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATIC_ROOT = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'modelCore.User'

LOGIN_REDIRECT_URL = '/backboard/home'

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"