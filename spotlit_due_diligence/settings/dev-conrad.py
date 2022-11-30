"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath, splitdrive

from .base import *
import os


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

########## END EMAIL CONFIGURATION




import dj_database_url
# test
# DATABASES = {
# 'default': dj_database_url.config(default='postgres://tkdgcgkheunkqu:m7hvpKFQikPRMDXKRj-7cq85fI@ec2-54-83-51-38.compute-1.amazonaws.com:5432/d71en0f703b4uj')
# }

# staging
# DATABASES = {
# 'default': dj_database_url.config(default='postgres://daxgxyraiomahk:GMew6fEnRV0Ly7nJ4Kzu4KnjEM@ec2-107-20-148-211.compute-1.amazonaws.com:5432/d7062tf5b2u0at')
# }

# production
# DATABASES = {
# 'default': dj_database_url.config(default='postgres://u9l6n0kf1b2sus:p8bfceuls45b3h7esstltud4qd8@ec2-50-17-194-125.compute-1.amazonaws.com:5482/dfvca3q87ir88v')
# }

# DATABASES['default']['OPTIONS']={'sslmode':'require'}

########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'comply_test',
        'USER': 'comply_dev',
        'PASSWORD': 'frisbeeisfun',
        'HOST': 'localhost',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

INSTALLED_APPS = ("longerusernameandemail",) + INSTALLED_APPS

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
    'django_nose'
)



TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
             '--with-coverage',
             '--cover-package=core',
             '--with-xunit'
             ]


MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)





DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION

SESSION_EXPIRE_AT_BROWSER_CLOSE=True

#Logo Local Settings
#SPOTLIT_LOGO= STATIC_URL+ '/img/spotlit-logo-app_4.png'
#SPOTLIT_FAVICON= STATIC_URL + '/img/'

#Encryption Key
ENCRYPTION_KEY = '{"hmacKey": {"hmacKeyString": "5kYRi4_t2OTCCSvekRNNAcNT17nElK8z2u2cTY-DaqA", "size": 256}, "aesKeyString": "sP79gsP6Qo8YcXfrEqW_Aw", "mode": "CBC", "size": 128}'
META_INFO ='{"encrypted": false, "versions": [{"status": "PRIMARY", "versionNumber": 1, "exportable": false}], "type": "AES", "name": "spotlit", "purpose": "DECRYPT_AND_ENCRYPT"}'
if(ENCRYPTION_KEY != ""):
    if(not os.path.isdir('encryption_keys')):
        os.mkdir('encryption_keys')
    fo = open("encryption_keys/1", "w")
    fo.write(ENCRYPTION_KEY)
    fo.close()

    meta = open('encryption_keys/meta', "w")
    meta.write(META_INFO)
    meta.close()

ENCRYPTED_FIELDS_KEYDIR = 'encryption_keys/'

SILENCED_SYSTEM_CHECKS = ["1_6.W002"]




MEDIA_ROOT = 'spotlit_due_diligence/media/'
MEDIA_URL = '/spotlit_due_diligence/media/'


# beat: python spotlit_due_diligence/manage.py celery beat --loglevel=info
# worker: python spotlit_due_diligence/manage.py celery worker --loglevel=info