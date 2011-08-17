from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template, redirect_to

from dajaxice.core import dajaxice_autodiscover

from apps.project_sheet.sitemaps import I4pProjectTranslationSitemap

# For server errors
handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

## Admin
admin.autodiscover()

## Sitemaps
sitemaps = {
    'projects': I4pProjectTranslationSitemap(),
    }

urlpatterns = patterns('',
    url(r'^', include('apps.i4p_base.urls')),
    url(r'^comment/', include('django.contrib.comments.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^project/', include('apps.project_sheet.urls')),
    url(r'^workgroup/', include('apps.workgroup.urls')),
    url(r'^partner/', include('apps.partner.urls')),
    url(r'^member/', include('apps.member.urls')),
    url(r'^feedback/', include('backcap.urls')),
    
    (r'^ajax_select/', include('ajax_select.urls')),

    # Static pages
    url(r'^beta/', redirect_to, {'url': '/', 'permanent': True}),
    url(r'^normal_index$', redirect_to, {'url': '/', 'permanent': True}),
    
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url('^robots\.txt$', include('robots.urls')),

    (r'^admin/', include(admin.site.urls)),
)

## Javascript i18n catalog
urlpatterns += patterns('',
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
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

urlpatterns += staticfiles_urlpatterns()

## i18n l10n translation UI
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

