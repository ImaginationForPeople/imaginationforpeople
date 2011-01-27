from django.conf import settings
#from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from transurlvania.defaults import *


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
 
# i18n l10n
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

if "privatebeta" in settings.INSTALLED_APPS:
    urlpatterns += lang_prefixed_patterns('',
        url(r'^beta/$', include('privatebeta.urls')),
        url(r'^beta/manifesto/$', direct_to_template, {'template': 'manifesto.html'}, name='manifesto'),
        url(r'^accounts/', include('userena.urls')),
    )
    urlpatterns += patterns('',
        (r'^$', redirect_to, {'url' : '/beta/'}),
        (r'^beta/', 'transurlvania.views.detect_language_and_redirect'),
    )
else:
    urlpatterns += lang_prefixed_patterns('',
        url(r'^$', direct_to_template, {'template': 'base.html'}, name='index'),
        url(r'^accounts/', include('userena.urls')),
    )
    urlpatterns += patterns('transurlvania.views',
        (r'^$', 'detect_language_and_redirect'),
    )



