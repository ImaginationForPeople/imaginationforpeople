from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import direct_to_template, redirect_to

from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover

# For server errors
handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

## Admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)

## DajaxIce (should be replaced by a static file once in production env)
dajaxice_autodiscover()

urlpatterns += patterns('',
    # Dajax(ice)
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)

## Static Media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
 
## i18n l10n translation UI
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

## Privatebeta
if "privatebeta" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^$', redirect_to, {'url':'/beta/'}),
        url(r'^beta/$', 'privatebeta.views.invite', name='privatebeta_invite'),
        url(r'^beta/sent/$', 'privatebeta.views.sent', name='privatebeta_sent'),
        url(r'^beta/manifesto/$', direct_to_template, {'template': 'manifesto.html'}, name='manifesto'),
        url(r'^beta/project-description/$', direct_to_template, {'template': 'project-description.html'}, name='project-description'),
    )
else:
    urlpatterns += patterns('',
        url(r'^$', direct_to_template, {'template': 'base.html'}, name='i4p-index'),
        url(r'^project/', include('apps.project_sheet.urls')),
        url(r'^accounts/', include('userena.urls')),
    )



