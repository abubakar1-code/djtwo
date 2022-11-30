"""Common settings and globals."""


from os.path import abspath, basename, dirname, join, normpath
from os import environ
from sys import path
from datetime import timedelta


########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Voyint Admin', 'admin@voyint.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION

########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/Chicago'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# Set survey URL
SURVEY_URL =  environ.get('SURVEY_URL', "")
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media')) + '/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = normpath(join(SITE_ROOT, 'media')) + '/'

REQUEST_UPLOAD_PATH = MEDIA_ROOT + 'uploads/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

STATIC_DIR = normpath(join(SITE_ROOT, 'static'))
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = r"x=i0jbu#)@c^r+jla(8#o4zliqz0fwb8l34b03())s1^m_44!b"
########## END SECRET CONFIGURATION


########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]
########## END SITE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'core.context_processors.global_settings',
    'core.context_processors.analytics',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    normpath(join(SITE_ROOT, 'templates')),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.FailedLoginMiddleware'
)
########## END MIDDLEWARE CONFIGURATION

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
# SECURE_SSL_REDIRECT = False
# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False

########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
#ROOT_URLCONF = '%s.urls' % SITE_NAME
ROOT_URLCONF = 'urls'
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'crispy_forms',
     'braces',
     'core',
     'localflavor',
     'django_countries',
     'eztables',
     'djangojs',
     'storages',
     'magic',
     'djangosecure',
     'encrypted_fields',
     'ho',
     'reportlab',
     'axes',
     'djcelery',
     'widget_tweaks'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
########## END WSGI CONFIGURATION



##crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

#login url
LOGIN_URL='/login'

#manager username
MANAGER_USERNAME='manager'
VOYINT_MANAGER_USERNAME = "info@voyint.com"
REQUEST_VOYINT_MANAGER_USERNAME = "manager@voyint.com"

#Logo
SPOTLIT_LOGO_NAME = 'img/spotlit-dashboard-logo.png'
SPOTLIT_LOGO= STATIC_URL + SPOTLIT_LOGO_NAME

SPOTLIT_FAVICON= STATIC_URL + ''

# Comply
COMPLY_LOGO_NAME = STATIC_DIR + "/img/voyint-logo-notagline.png"
COMPLY_LOGO = STATIC_URL + COMPLY_LOGO_NAME

COMPLY_EMAIL_LOGO_NAME = STATIC_DIR + "/img/voyint-logo-notagline.png"
COMPLY_EMAIL_LOGO = STATIC_URL + COMPLY_EMAIL_LOGO_NAME


#Comply Report Images
COMPLY_LOGO_FOR_PDF = STATIC_DIR + "/img/voyint-logo-notagline.png"
COMPLY_GREY_BAR = STATIC_DIR + "/img/report/comply_grey_bar.jpg"



#Report Images

ASHTREE_LOGO_FOR_PDF = STATIC_DIR + "/img/report/header_ashtree.jpg"
WATERMARK=STATIC_DIR + ""
HORIZONTAL_LINE=STATIC_DIR + "/img/report/green-bar-comply.jpg"
HORIZONTAL_LINE_ASHTREE=STATIC_DIR + "/img/report/green-bar.jpg"
# LAST_PAGE=STATIC_DIR + "/img/report/last-report-page-comply.jpg"

LAST_PAGE=STATIC_DIR + "/img/report/comply_backpage_5_24.jpg"

LAST_PAGE_ASHTREE=STATIC_DIR + "/img/report/last-report-page_ashtree.jpg"
LAST_PAGE_CLIENT=STATIC_DIR + "/img/report/last-report-page-client.jpg"
FONT_DIR=STATIC_DIR + "/img/open-sans/"
BULLET=STATIC_DIR + "/img/report/green-bullet.jpg"
FLAG=STATIC_DIR + "/img/report/flag.jpg"
YELLOW_FLAG=STATIC_DIR + "/img/report/yellow-flag.png"
BULLET_ASHTREE=STATIC_DIR + "/img/report/bullet_ashtree.jpg"
X=STATIC_DIR + "/img/report/alert.jpg"
NO_RED_FLAG=STATIC_DIR + "/img/report/no-red-flags.jpg"
PRESCIENT=STATIC_DIR + "/img/report/a_prescient_company.jpg"
WATERMARK_ASHTREE=STATIC_DIR + "/img/report/bg_ashtree.jpg"

# Voyint
VOYINT_BULLET=STATIC_DIR + "/img/report/blue-bullet.png"
VOYINT_HORIZONTAL_LINE=STATIC_DIR + "/img/report/blue-bar.png"
VOYINT_LAST_PAGE=STATIC_DIR + "/img/report/voyint_backpage.jpg"
VOYINT_LOGO=STATIC_DIR + "/img/voyint-logo-notagline.png"

#Password reset timeout link config
PASSWORD_RESET_TIMEOUT_DAYS = 10


# Django-axes config
AXES_LOGIN_FAILURE_LIMIT = 50
AXES_COOLOFF_TIME = timedelta(seconds=1800)
AXES_LOCKOUT_TEMPLATE = 'core/lockout.html'

#########S3 Configuration######
if environ.get('ENV','') == "PROD" and bool(int(environ.get('DJANGO_S3', "1"))) == True:
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

#AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
