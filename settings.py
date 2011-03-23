# -*- coding:utf-8 -*-

import os
import sys
import socket
from django.utils.translation import ugettext_lazy as _
# Django settings for i4p project.

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_ROOT,'..'))

# If we are on staging, then switch off debug
if socket.gethostname() == 'i4p-dev':
    DEBUG = False
else:
    DEBUG = True

# if you need to debug privatebeta, use this
FORCE_PRIVATEBETA = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Simon Sarazin', 'simonsarazin@imaginationforpeople.com'),
    ('Guillaume Libersat', 'guillaume@fuzzyfrequency.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT,'i4p.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

## Project path
PROJECT_PATH = os.path.abspath('%s' % os.path.dirname(__file__))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
  ('en', u'English'),
  ('fr', u'Français'),
  ('es', u'Español'),
  ('pt', u'Português'),
  ('de', u'German'),
  ('it', u'Italian'),
  ('ru', u'Russian'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-m2v@6wb7+$!*nsed$1m5_f=1p5pf-lg^_m3+@x*%fl5a$qpqd'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
     
    'reversion.middleware.RevisionMiddleware',

    'request.middleware.RequestMiddleware',

    'userena.middleware.UserenaLocaleMiddleware',

    'localeurl.middleware.LocaleURLMiddleware', 
    
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

if not DEBUG:
    MIDDLEWARE_CLASSES += (
		'privatebeta.middleware.PrivateBetaMiddleware',
	)


AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
#    "mothertongue.context_processors.router",
)


ROOT_URLCONF = 'imaginationforpeople.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    # External Apps
    'localeurl',
    'dajaxice',
    'dajax',
    'south',
    'django_nose',
    'lettuce.django',
    'django_extensions',
    'userena',
    'guardian',
    'debug_toolbar',
    'rosetta',
    'tagging',
    'imagekit',
    'contact_form',
    'request',
    'oembed_works',
    'reversion',
    'django_countries',
    'licenses',
               
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',

    # Internal Apps
    'apps.i4p_base',
    'apps.member',
    'apps.project_sheet'
)

OEMBED_PROVIDERS = {
  'YouTube': ('http://www.youtube.com/oembed/', 
              [r'http://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9\-=_]{11}']),
  'Vimeo': ('http://vimeo.com/api/oembed.json',
            [r'http://(?:www\.)?vimeo\.com/\d+']),
  'Dailymotion': ('http://www.dailymotion.com/services/oembed/?wmode=transparent',
                  [r'http://(?:www\.)?dailymotion\.com/video/\S+']),
   'Flickr': ('http://www.flickr.com/services/oembed',
              [r'http://(?:www\.)?flickr\.com/photos/\S+?/(?:sets/)?\d+/?']),
}


if not DEBUG or FORCE_PRIVATEBETA:
	INSTALLED_APPS += (
		'privatebeta',
		)

USERENA_WITHOUT_USERNAMES = True

# localeurl/monther-tongue
PREFIX_DEFAULT_LOCALE = True
LOCALEURL_USE_ACCEPT_LANGUAGE = True


### Lettuce
LETTUCE_APPS = (
    'apps',
)

#Userena
ANONYMOUS_USER_ID=-1
AUTH_PROFILE_MODULE='member.I4pProfile'

### Nose test runner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

### Debug-tool-bar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)



### Mailer
SERVER_EMAIL = 'noreply@imaginationforpeople.com'
DEFAULT_FROM_EMAIL = SERVER_EMAIL
# Write emails to console if in development mode
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# else, use SMTP
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 25
    EMAIL_SUBJECT_PREFIX = '[ImaginationForPeople]'

### Private Beta
PRIVATEBETA_REDIRECT_URL = '/beta/'
PRIVATEBETA_ALWAYS_ALLOW_VIEWS = ('django.views.generic.simple.direct_to_template',
				  'django.views.generic.simple.redirect_to',)
PRIVATEBETA_ALWAYS_ALLOW_MODULES = ('django.contrib.admin.sites',
				    'contact_form.views')

### Dajax Ice
DAJAXICE_MEDIA_PREFIX = "js/dajax"
DAJAXICE_XMLHTTPREQUEST_JS_IMPORT = True
DAJAXICE_JSON2_JS_IMPORT = True
DAJAXICE_DEBUG = DEBUG

## Ignore dajax ice path
import re
LOCALE_INDEPENDENT_PATHS = (
	re.compile('^/js/dajax/.*$'),
	)

