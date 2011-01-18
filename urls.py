from django.conf import settings
#from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from transurlvania.defaults import *


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = lang_prefixed_patterns('',
    (r'^beta/', include('privatebeta.urls')),
    #url(r'^$', direct_to_template, {'template' : 'base.html'}, name="i4p-index"),
    (r'^accounts/', include('userena.urls')),
)

# Static pages
urlpatterns += lang_prefixed_patterns('django.views.generic.simple',
    url(r'^manifesto$', 'direct_to_template', {'template': 'manifesto.html'}, name='manifesto'),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)

# Serve static files if in debug mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

