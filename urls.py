from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin


from dynamicsites.views import site_info
#from i18nurls.i18n import i18n_patterns # XXX: update when moving to dj1.4
from userena.contrib.umessages import views as messages_views

from apps.member.forms import AutoCompleteComposeForm
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

urlpatterns = i18n_patterns('',
                            )

## Static Media
if settings.DEBUG:
    urlpatterns += patterns('',
      (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
      (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
      url(r'^site-info$', site_info),
    )

urlpatterns += i18n_patterns('',
#    url(r'^', include('apps.i4p_base.urls')),

    url(r'^comment/', include('django.contrib.comments.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^project/', include('apps.project_sheet.urls')),
    url(r'^workgroup/', include('apps.workgroup.urls')),
    url(r'^partner/', include('apps.partner.urls')),
    url(r'^member/', include('apps.member.urls')),
    url(r'^feedback/', include('backcap.urls')),
    url(r'^forum/', include('apps.forum.urls')),

    # Configure umessages compose view so that it uses recipient autocompletion
    url(r'^messages/compose/$',
        messages_views.message_compose,
        kwargs={'compose_form': AutoCompleteComposeForm},
        name='userena_umessages_compose'),
    # Form at the bottom of message list doesn't use autocompletion
    url(r'^messages/reply/$',
        messages_views.message_compose,
        name='userena_umessages_reply'),
    url(r'^messages/', include('userena.contrib.umessages.urls')),

    (r'^newsletters/', include('emencia.django.newsletter.urls')),
    
    #(r'^ajax_select/', include('ajax_select.urls')),
	url(r'^ajax_lookup/(?P<channel>[-\w]+)/$',
		'ajax_select.views.ajax_lookup',
        name = 'ajax_lookup'
    ),
    url(r'^add_popup/(?P<app_label>\w+)/(?P<model>\w+)/$',
        'ajax_select.views.add_popup',
        name = 'add_popup'
    ),

    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),                             
                             
)

## Non localized urls
urlpatterns += patterns('',
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^tinymce/', include('tinymce.urls')),
    (r'^uploadify/', include('uploadify.urls')),

    url('^robots\.txt$', include('robots.urls')),
                        
    url(r'^admin/filebrowser/', include('filebrowser.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

## CMS
urlpatterns += i18n_patterns('',
                        url(r'^', include('cms.urls'))
                        )
