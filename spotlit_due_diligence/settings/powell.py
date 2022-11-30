"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath

from .base import *
import dj_database_url
import os


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'post_office.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
#EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST = environ.get('SENDGRID_EMAIL_HOST', 'smtp.sendgrid.net')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('SENDGRID_EMAIL_HOST_PASSWORD', '')


# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('SENDGRID_EMAIL_HOST_USER', 'apikey')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

########## END EMAIL CONFIGURATION

# ######### PROD DATABASE CONFIGURATION
if environ.get('ENV','') == "PROD" or environ.get('ENV','') == "STAGING":
    DATABASES = {'default': dj_database_url.config()}
########## END PROD DATABASE CONFIGURATION
else:
    ########## DATABASE CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
    DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'voyint',
    'USER': 'node',
    'PASSWORD': 'node',
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

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
             '--with-coverage',
             '--cover-package=core',
             '--with-xunit'
             ]


if DEBUG:
   INTERNAL_IPS = ('127.0.0.1', 'localhost',)
   MIDDLEWARE_CLASSES += (
       'debug_toolbar.middleware.DebugToolbarMiddleware',
   )

   INSTALLED_APPS += (
       'debug_toolbar',
   )

   DEBUG_TOOLBAR_PANELS = [
       'debug_toolbar.panels.versions.VersionsPanel',
       'debug_toolbar.panels.timer.TimerPanel',
       'debug_toolbar.panels.settings.SettingsPanel',
       'debug_toolbar.panels.headers.HeadersPanel',
       'debug_toolbar.panels.request.RequestPanel',
       'debug_toolbar.panels.sql.SQLPanel',
       'debug_toolbar.panels.staticfiles.StaticFilesPanel',
       'debug_toolbar.panels.templates.TemplatesPanel',
       'debug_toolbar.panels.cache.CachePanel',
       'debug_toolbar.panels.signals.SignalsPanel',
       'debug_toolbar.panels.logging.LoggingPanel',
       'debug_toolbar.panels.redirects.RedirectsPanel',
   ]

   DEBUG_TOOLBAR_CONFIG = {
       'INTERCEPT_REDIRECTS': False,
   }

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
# INTERNAL_IPS = ('127.0.0.1',)
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
