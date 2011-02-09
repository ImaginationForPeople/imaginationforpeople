from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to


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
    urlpatterns += patterns('',
        url(r'^$', redirect_to, {'url':'/beta/'}),
        url(r'^beta/$', 'privatebeta.views.invite', name='privatebeta_invite'),
        url(r'^beta/sent/$', 'privatebeta.views.sent', name='privatebeta_sent'),
        url(r'^beta/manifesto/$', direct_to_template, {'template': 'manifesto.html'}, name='manifesto'),
    )
else:
    urlpatterns += patterns('',
        url(r'^$', direct_to_template, {'template': 'base.html'}, name='i4p-index'),
        url(r'^project/', include('apps.project_sheet.urls')),
        url(r'^accounts/', include('userena.urls')),
    )



