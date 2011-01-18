from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^beta/', include('privatebeta.urls')),


    url(r'^$', direct_to_template, {'template' : 'base.html'}, name="i4p-index"),
    (r'^accounts/', include('userena.urls')),
    
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)


# Static pages
urlpatterns += patterns('django.views.generic.simple',
    url(r'^manifesto$', 'direct_to_template', {'template': 'manifesto.html'}, name='manifesto'),
)

# Serve static files if in debug mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

