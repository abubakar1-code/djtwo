"""Production settings and globals."""

from __future__ import absolute_import

from os import environ

from .base import *

import dj_database_url
import os

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

########## HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = ['spotlit.herokuapp.com','app.spotlit.com', 'calm-island-7971.herokuapp.com', 'thawing-beach-3596.herokuapp.com', 'spotlit-test.herokuapp.com', 'spotlit-staging.herokuapp.com', 'comply.prescient.com','comply-staging.prescient.com']
########## END HOST CONFIGURATION

INSTALLED_APPS = ("longerusernameandemail",) + INSTALLED_APPS

DEBUG = os.environ.get('DJANGO_DEBUG', False)
TEMPLATE_DEBUG = DEBUG

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'post_office.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
#EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.office365.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'admin@spotlit.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {'default': dj_database_url.config()}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
########## END CACHE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('SECRET_KEY')
########## END SECRET CONFIGURATION

#########S3 Configuration######
if bool(int(environ.get('DJANGO_S3', "1"))) == True:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_S3_REGION_NAME = environ.get("BUCKETEER_AWS_REGION")
    AWS_ACCESS_KEY_ID = environ.get('BUCKETEER_AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = environ.get('BUCKETEER_BUCKET_NAME')
    S3_URL = 'https://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com'
    MEDIA_ROOT = ''
    MEDIA_URL = S3_URL + '/'
    AWS_QUERYSTRING_AUTH = False
    AWS_HEADERS = {'x-amz-server-side-encryption':'AES256'}

#settings for HTTPS
#secure cookies
CSRF_COOKIE_SECURE=True
SESSION_EXPIRE_AT_BROWSER_CLOSE=True

#django secure settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_FRAME_DENY=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True


#Encryption Key
ENCRYPTION_KEY = environ.get('ENCRYPTION_KEY', '')
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

MANAGER_USERNAME=os.environ.get('MANAGER_USERNAME', 'manager')

#Google Analytics. Added in Heroku environment varibales
GOOGLE_ANALYTICS_KEY = os.environ.get('GOOGLE_ANALYTICS_KEY', '')
