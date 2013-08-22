# -*- coding:utf-8 -*-
# Django settings for imaginationforpeople project.

import os
import re
import sys
import site

import askbot
import djcelery

from django.utils.translation import ugettext_lazy as _

import apps.i4p_base.mdx_i4p as mdx_i4p

# Default values for site_settings

OVERRIDE_CACHE_BACKEND = None
GEONAMES_USERNAME = None
MAPQUEST_API_KEY = None

# Import settings for the given site
from site_settings import *

#from django.utils.translation import gettext
gettext = lambda s: s

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_ROOT, '..'))

ASKBOT_ROOT = os.path.abspath(os.path.dirname(askbot.__file__))
site.addsitedir(os.path.join(ASKBOT_ROOT, 'deps'))

ADMINS = (
    ('Support', 'support@imaginationforpeople.org'),
    ('Sylvain Maire', 'sylvainmaire@imaginationforpeople.org'),
    ('Guillaume Libersat', 'guillaumelibersat@imaginationforpeople.org'),
    ('Alban Tiberghien', 'albantiberghien@imaginationforpeople.org'),
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
  ('zh-cn', u'中文'),
)

CMS_LANGUAGES = {
    1: [
        {
            'code': 'en',
            'name': u'English',
            'fallbacks': ['fr', 'de'],
        },
        {
            'code': 'fr',
            'name': u'Français',
            'fallbacks': ['en', 'es'],
        },
        {
            'code': 'el',
            'name': u'Ελληνικά',
        },
        {
            'code': 'es',
            'name': u'Español',
            'fallbacks': ['fr', 'en'],
        },
        {
            'code': 'pt',
            'name': u'Português',
        },
        {
            'code': 'de',
            'name': u'Deutsch',
        },
        {
            'code': 'it',
            'name': u'Italiano',
            'fallbacks': ['fr', 'en', 'es'],
        },
        {
            'code': 'ru',
            'name': u'Русский',
        },
        {
            'code': 'zh',
            'name': u'中文',
        },
    ],
    'default': {
        'fallbacks': ['en', 'fr', 'es'],
        'redirect_on_fallback': False,
        'public': True,
        'hide_untranslated': False,
    }
} 

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
CACHE_PREFIX ='imaginationforpeople'

# Cache
if OVERRIDE_CACHE_BACKEND:
    CACHES = {
    'default': OVERRIDE_CACHE_BACKEND,
    'askbot': OVERRIDE_CACHE_BACKEND
    }
else:
    if DEBUG:
        CACHES = {
        'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
        'askbot': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
        }
    else:
        CACHES = {
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
        'askbot': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
        }

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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

	#below is askbot stuff for this tuple
    'askbot.middleware.view_log.ViewLogMiddleware',
    'askbot.middleware.anon_user.ConnectToSessionMessagesMiddleware',
    'askbot.middleware.forum_mode.ForumModeMiddleware',
    'askbot.middleware.cancel.CancelActionMiddleware',
    'django.middleware.transaction.TransactionMiddleware',

    'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',

)

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'apps.i4p_base.middleware.profile.ProfileMiddleware',
    )
    LETTUCE_APPS = (
            'apps.member',
            'apps.project_sheet',
            'apps.i4p_base',
            )

if 'DEBUG_PROFILE_MIDDLEWARE_ENABLED' in locals() and DEBUG_PROFILE_MIDDLEWARE_ENABLED == True:
    MIDDLEWARE_CLASSES += (
        'apps.i4p_base.middleware.profile.ProfileMiddleware',
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
    'apps.i4p_base.context_processors.search_form',
    'apps.i4p_base.context_processors.settings',
    'apps.member.context_processors.member_forms',

    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
    
    'dynamicsites.context_processors.current_site',
    
    'askbot.context.application_settings',
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
    'hvad',
    'honeypot',
    'serializers',
    'tabs',
    'logentry_admin',
    'django_lamson',

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

    'actstream',
    
    'django_notify',
    'wiki',
    'wiki.plugins.notifications',
    'wiki.plugins.attachments',
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
    'autocomplete_light',
    
    'zinnia',
    'cmsplugin_zinnia',
    
    'cms.plugins.text',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.picture',
    'cms.plugins.googlemap',
    'cms.plugins.video',
    #Deprecated, remove me as soon as all data has been removed
    'cms.plugins.twitter',
    'cms.plugins.teaser',
    'cms.plugins.snippet',
    'cmsplugin_facebook',
    'cmsplugin_iframe',
    'cmsplugin_contact',
    'cmsplugin_twitter',

    'askbot.deps.livesettings',
    'askbot',
    
    'longerusername',
    'keyedcache',
    'djcelery',
    'djkombu',
    'followit',
    'tastypie',

    'categories',
    'categories.editor',

    'django.contrib.gis',
    'leaflet',
    'floppyforms',
    
    # Internal Apps
    'apps.forum',
    'apps.i4p_base',
    'apps.member',
    'apps.project_sheet',
    'apps.project_support',
    'apps.partner',
    'apps.workgroup',
    'apps.tags',
    'apps.forum',
    'apps.map',
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
USERENA_MUGSHOT_GRAVATAR = True

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
    'debug_toolbar.panels.sql.SQLDebugPanel',
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
LOGOUT_URL = "/member/signout/"

# XXX To be removed as soon as google login is confirmed working
LOCALE_INDEPENDENT_PATHS = (
        re.compile('^/member/complete/google-oauth2/?'),
        re.compile('^/member/login/google-oauth2/?'),
	)

## Flags
COUNTRIES_FLAG_URL = 'images/flags/%(code)s.gif'

### HAYSTACK
if (not DEBUG) or USESOLR:
   HAYSTACK_CONNECTIONS = {
       'default': {
           'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
          'URL': 'http://127.0.0.1:8983/solr',           
       },
   }
elif DEBUG:
   HAYSTACK_CONNECTIONS = {
       'default': {
         'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
         'PATH': os.path.join(PROJECT_ROOT, 'i4p_index'),
         'STORAGE': 'file',
         'POST_LIMIT': 128 * 1024 * 1024,
         'INCLUDE_SPELLING': True,
         'BATCH_SIZE': 500,
       },
   }

HAYSTACK_ITERATOR_LOAD_PER_QUERY = 99999999

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
    ('compiled_images', os.path.join(STATIC_ROOT, 'compiled_images')),
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
TINYMCE_DEFAULT_CONFIG = {
                          'theme': "advanced",
                          'plugins': 'contextmenu,table,template,paste',
                          'relative_urls': False,
                          'remove_script_host': 0,
                          'convert_urls': False,
                          'width': '90%',
                          'height': '300px',
                          'theme_advanced_blockformats' : 'p,div,h1,h2,h3,h4,h5,h6,blockquote,dt,dd',
                          'theme_advanced_buttons1_add' : 'fontsizeselect,fontselect,formatselect,forecolor', 
                          'theme_advanced_buttons2_add' : 'blockquote,pasteword', 
                          'theme_advanced_buttons3_add' : 'tablecontrols,template',     
                          'template_external_list_url' : '/admin/tinymce/templates/',   
                          }
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
  ('pages/popups_notifications.html', _('Popups and notifications container')),
)

CMS_REDIRECTS = True
CMS_SOFTROOT = True
CMS_SEO_FIELDS = True

APPEND_SLASH = True

RECAPTCHA_USE_SSL = True

## Askbot
ASKBOT_URL = 'forum' # without leading and trailing slashes
ASKBOT_STARTUP_CHECK = False
ALLOW_UNICODE_SLUGS = False
ASKBOT_USE_STACKEXCHANGE_URLS = False 
ASKBOT_SKINS_DIR = os.path.join(PROJECT_ROOT, 'apps/forum/templates')
LIVESETTINGS_CACHE_TIMEOUT = 6000
KEYEDCACHE_ALIAS = "askbot"
CACHE_TIMEOUT = LIVESETTINGS_CACHE_TIMEOUT
ASKBOT_DEBUG_INCOMING_EMAIL = DEBUG

## REPLY BY MAIL IN ASKBOT 
LAMSON_RECEIVER_CONFIG = {'host': '127.0.0.1', 'port': 8025}
LAMSON_HANDLERS = ['askbot.mail.lamson_handlers']
LAMSON_ROUTER_DEFAULTS = {'host': '.+'}


## Celery Settings
# TODO: fill the admin doc : ./manage.py celeryd -l ERROR --purge
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
# If this is True, all tasks will be executed locally by blocking until the task returns. 
# tasks will be executed locally instead of being sent to the queue.
CELERY_ALWAYS_EAGER = DEBUG

djcelery.setup_loader()

# HVAD (yes, it's still prefixed with 'NANI')
NANI_TABLE_NAME_SEPARATOR = ''

# ACTIVITY STREAM
ACTSTREAM_SETTINGS = {
    'MODELS': ('project_sheet.I4pProject', 'project_sheet.I4pProjectTranslation', 'auth.User', 'project_sheet.Answer'),
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'GFK_FETCH_DEPTH': 1,
}



# WIKI
markdown_i4p = mdx_i4p.makeExtension()
WIKI_MARKDOWN_EXTENSIONS = ['extra', 'toc', markdown_i4p]

#LEAFLET
LEAFLET_CONFIG = {
    'TILES_URL': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'PLUGINS': {
        'markercluster': {
            'css': [os.path.join(STATIC_URL, 'css/MarkerCluster.css'), 
                    os.path.join(STATIC_URL, 'css/MarkerCluster.Default.css')],
            'js': os.path.join(STATIC_URL, 'js/leaflet.markercluster.js'),
        },
    }
}

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
        'handlers': ['console'],
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
 	# Uncomment this if you don't use sentry
        #'mail_admins': {
        #    'level': 'ERROR',
        #    'filters': ['require_debug_false'],
        #    'class': 'django.utils.log.AdminEmailHandler'
        #},
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'WARNING',
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
        #'django.request': {
        #    'handlers': ['mail_admins'],
        #    'level': 'ERROR',
        #    'propagate': True,
        #},
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
