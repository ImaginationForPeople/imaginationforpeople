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
       
urlpatterns += lang_prefixed_patterns('',
    url(r'^$', include('privatebeta.urls')),
    url(r'^beta/$', direct_to_template, {'template' : 'privatebeta/base.html'}, name="i4p-index"),
    url(r'^manifesto/', direct_to_template, {'template': 'manifesto.html'}, name='manifesto'),
    url(r'^accounts/', include('userena.urls')),
)

urlpatterns += patterns('transurlvania.views',
    (r'^$', 'detect_language_and_redirect'),
)



