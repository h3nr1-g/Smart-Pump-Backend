from .common import *

DEBUG = False

SECRET_KEY = 'TOPSECRET1234'

ALLOWED_HOSTS = ['*']

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


DATABASES = {
 'default': {
     'ENGINE': 'django.db.backends.mysql',
     'NAME': 'smartpump_prod',
     'USER': 'root',
     'PASSWORD': 'foobar',
     'HOST': 'MYSQL-HOST.net',
     'PORT': '3306',
     'OPTIONS': {
         'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
     },
 }
}
