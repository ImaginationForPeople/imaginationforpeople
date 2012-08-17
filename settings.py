# -*- coding:utf-8 -*-
# Django settings for imaginationforpeople project.

import os
import re
import sys
from django.utils.translation import ugettext_lazy as _

# Import settings for the given site
from site_settings import *

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_ROOT, '..'))

ADMINS = (
    ('Simon Sarazin', 'simonsarazin@imaginationforpeople.org'),
    ('Sylvain Maire', 'sylvainmaire@imaginationforpeople.org'),
    ('Guillaume Libersat', 'guillaumelibersat@imaginationforpeople.org'),
    ('Alban Tiberghien', 'albantiberghien@imaginationforpeople.org'),
    ('Vincent Charrier', 'vincentcharrier@imaginationforpeople.org'),
)

MANAGERS = (
    ('IP Team', 'team@imaginationforpeople.org'),
)

## Project path
PROJECT_PATH = os.path.abspath('%s' % os.path.dirname(__file__))

## Dynamicsites
SITES_DIR = os.path.join(PROJECT_ROOT, 'sites')

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
  ('el', u'Ελληνικά'),
  ('es', u'Español'),
  ('pt', u'Português'),
  ('de', u'Deutsch'),
  ('it', u'Italiano'),
  ('ru', u'Русский'),
  ('zh', u'中文'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media/')


# Make this unique, and don't share it with anybody.
SECRET_KEY = '-m2v@6wb7+$!*nsed$1m5_f=1p5pf-lg^_m3+@x*%fl5a$qpqd'

# Cache
if DEBUG:
    CACHE_BACKEND = 'django.core.cache.backends.dummy.DummyCache'
else:
    CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
CACHES = {
    'default': {
        'BACKEND': CACHE_BACKEND,
    }
}

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',


    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'dynamicsites.middleware.DynamicSitesMiddleware',
     ## The order of these locale middleware classes matters
    # Language selection based on profile
    # URL based language selection (eg. from top panel)
    # We don't use django cms one, for compatibility reasons
    'django.middleware.locale.LocaleMiddleware',
    # CommonMiddleware MUST come after LocaleMiddleware, otherwise, 
    # url matching will not work properly
    'django.middleware.common.CommonMiddleware',
    #'userena.middleware.UserenaLocaleMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',

    'reversion.middleware.RevisionMiddleware',



    'honeypot.middleware.HoneypotMiddleware',

    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',

    'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    LETTUCE_APPS = (
            'apps.member',
            'apps.project_sheet',
            'apps.i4p_base',
            )

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.OpenIDBackend',
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'backcap.context_processors.backcap_forms',

    'django.core.context_processors.static',
    'apps.project_sheet.context_processors.project_search_forms',
    'apps.member.context_processors.member_forms',

    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
    
    'dynamicsites.context_processors.current_site',
)


ROOT_URLCONF = 'imaginationforpeople.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'apps/member/templates'),
    os.path.join(PROJECT_PATH, 'apps/i4p_base/templates'),
    os.path.join(PROJECT_PATH, 'apps/project_sheet/templates'),
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    # External Apps
    'dynamicsites',
    'south',
    'django_nose',
    'django_extensions',
    'userena',
    'userena.contrib.umessages',
    'guardian',
    'nani',
    'honeypot',

    'raven.contrib.django',

    'tinymce',
    'tagging',
    'imagekit',
    'oembed_works',
    'reversion',
    'django_countries',
    'easy_thumbnails',
    'licenses',
    'haystack',
    'voting',
    'notification',
    'backcap',
    'compressor',
    'robots',
    'ajax_select',
    'ajaxcomments',
    'django_mailman',
    'linaro_django_pagination',
    'template_utils',
    'simplegravatar',
    'social_auth',


    #'grappelli',
    'filebrowser',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.syndication',
    'django.contrib.redirects',

    'emencia.django.newsletter',
    'emencia.django.newsletter.cmsplugin_newsletter',    
    'cms',
    'mptt',
    'menus',
    'sekizai',
    'cms.plugins.text',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.picture',
    'cms.plugins.googlemap',
    'cms.plugins.video',
    'cms.plugins.twitter',
    'cms.plugins.teaser',
    'cms.plugins.snippet',

    'cmsplugin_facebook',

    # Internal Apps
    'apps.i4p_base',
    'apps.member',
    'apps.project_sheet',
    'apps.partner',
    'apps.workgroup',
)

# django-ajax_select
AJAX_LOOKUP_CHANNELS = {
    'members' : ('apps.member.lookups', 'UserLookup'),
}
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'


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

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
        'lettuce.django',
        )


## Userena
USERENA_WITHOUT_USERNAMES = True
USERENA_MUGSHOT_DEFAULT = 'monsterid'
USERENA_MUGSHOT_SIZE = 160
USERENA_MUGSHOT_PATH = 'mugshots/'

USERENA_DEFAULT_PRIVACY = 'open'

## Social auth
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_location', 'user_website',
                                 'user_work_history']
GOOGLE_OAUTH_EXTRA_SCOPE = ['https://www.googleapis.com/auth/userinfo.profile']

# Catch social auth exceptions even in debug mode
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'apps.member.social.create_user',
    'apps.member.social.associate_user', # Override default pipeline function
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)

# Honeypot
HONEYPOT_FIELD_NAME = "homepage"

# Userena
ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'member.I4pProfile'

### Nose test runner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

### Debug-tool-bar
INTERNAL_IPS = ('127.0.0.1', '192.168.0.18')
DEBUG_TOOLBAR_CONFIG = {
    # useful for testing dynamicsites
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    #'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)


### Tagging
FORCE_LOWERCASE_TAGS = True

### Mailer
SERVER_EMAIL = 'noreply@imaginationforpeople.org'

DEFAULT_FROM_EMAIL = SERVER_EMAIL

if not 'EMAIL_SUBJECT_PREFIX' in locals():
    EMAIL_SUBJECT_PREFIX = '[ImaginationForPeople] '

# Write emails to console if in development mode
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# else, use SMTP
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 25


## LOG IN
LOGIN_REDIRECT_URL = '/'
USERENA_SIGNIN_REDIRECT_URL = '/'
LOGIN_URL = "/member/signin/"

# XXX To be removed as soon as google login is confirmed working
LOCALE_INDEPENDENT_PATHS = (
        re.compile('^/member/complete/google-oauth2/?'),
	)

## Flags
COUNTRIES_FLAG_URL = 'images/flags/%(code)s.gif'

### HAYSTACK
HAYSTACK_SITECONF = 'imaginationforpeople.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_PATH, 'i4p_index')

### STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    
    # For dynamic sites
    'sites.finders.SiteDirectoriesFinder',

    # Compressor finder
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = (
    ('js', os.path.join(STATIC_ROOT, 'js')),
    ('css', os.path.join(STATIC_ROOT, 'css')),
    ('css', os.path.join(STATIC_ROOT, 'compiled_sass')),
    ('fonts', os.path.join(STATIC_ROOT, 'fonts')),
    ('images', os.path.join(STATIC_ROOT, 'images')),
)

COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
    )

### COMPRESOR
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

## Backcap config
BACKCAP_NOTIFY_WHOLE_STAFF = False
BACKCAP_NOTIFIED_USERS = ['GuillaumeLibersat',
                          'SimonSarazin',
                          'AlbanTiberghien']


## TINYMCE
TINYMCE_DEFAULT_CONFIG = {'theme': "advanced",
                          'relative_urls': False,
                          'remove_script_host': 0,
                          'convert_urls': False,
                          'plugins': "contextmenu",
                          'width': '90%',
                          'height': '300px'}
TINYMCE_FILEBROWSER = True
FILEBROWSER_USE_UPLOADIFY = False

## Newsletter
DEFAULT_HEADER_SENDER = "Imagination For People Newsletter <contact@imaginationforpeople.org>"

## CMS
CMS_PERMISSION = True

CMS_TEMPLATES = (
  ('pages/homepage.html', _('Homepage')),
  ('pages/flatpage.html', _('Black Page')),
  ('pages/contrib.html', _('Contribution page')),
  ('pages/onemenu.html', _('One menu page')),
)

CMS_REDIRECTS = True
CMS_HIDE_UNTRANSLATED = False
CMS_SOFTROOT = True
CMS_SEO_FIELDS = True

APPEND_SLASH = True

NANI_TABLE_NAME_SEPARATOR = ''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}