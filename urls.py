from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template, redirect_to

import contact_form.views as contact_form_views

from dajaxice.core import dajaxice_autodiscover

# For server errors
handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

## Admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('apps.i4p_base.urls')),
    url(r'^comment/', include('django.contrib.comments.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^project/', include('apps.project_sheet.urls')),
    url(r'^member/', include('apps.member.urls')),
    url(r'^feedback/', include('backcap.urls')),

    # Static pages
    url(r'^pages/manifesto/$', direct_to_template, {'template': 'manifesto.html'}, name='manifesto'),
    url(r'^pages/project-description/$', direct_to_template, {'template': 'project-description.html'}, name='project-description'),
    url(r'^pages/contact/$', contact_form_views.contact_form, name='contact_form'),
    url(r'^pages/contact/sent$', redirect_to, {'url': '/beta/sent/', 'permanent': False}, name='contact_form_sent'),

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

urlpatterns += staticfiles_urlpatterns()

## i18n l10n translation UI
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

