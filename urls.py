from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import autocomplete_light
from django.views.generic.base import TemplateView
autocomplete_light.autodiscover() # Keep this before admin.autodiscover()

from askbot.sitemap import QuestionsSitemap
from dynamicsites.views import site_info
from django_notify.urls import get_pattern as get_notify_pattern
from userena.contrib.umessages import views as messages_views
from wiki.urls import get_pattern as get_wiki_pattern
from filebrowser.sites import site

from apps.member.forms import AutoCompleteComposeForm
from apps.project_sheet.sitemaps import I4pProjectTranslationSitemap
from apps.map.views import ProjectListJsonView, ProjectCardAjaxView
from apps.tags.sitemaps import TagSitemap


# For server errors
handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

## Admin
admin.autodiscover()

import haystack.views

import apps.i4p_base.ajax
import apps.i4p_base.views

## Sitemaps
sitemaps = {
    'projects': I4pProjectTranslationSitemap(),
    'questions': QuestionsSitemap(),
    'tags': TagSitemap(),
}

urlpatterns = i18n_patterns('',

)

## Static Media
if settings.DEBUG:
    urlpatterns += patterns('',
      (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
      url(r'^site-info$', site_info),
    )
    
    urlpatterns += staticfiles_urlpatterns()
    
    
##Zinia (blog)
urlpatterns += i18n_patterns('',
                        url(r'^blog/', include('zinnia.urls')),
                        )

urlpatterns += i18n_patterns('',
    url(r'^', include('apps.i4p_base.urls')),

    url(r'^comment/', include('django.contrib.comments.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^project/', include('apps.project_sheet.urls')),
    
    url(r'^projects/map/$', TemplateView.as_view(template_name='map/global_map.html')),
    url(r'^projects.json$', ProjectListJsonView.as_view(), name='projects-json'),
    url(r'^get-project-card$', ProjectCardAjaxView.as_view(), name='get-project-card'),
    
    url(r'^group/', include('apps.workgroup.urls')),
    url(r'^partner/', include('apps.partner.urls')),
    url(r'^member/', include('apps.member.urls')),
    url(r'^tags/', include('apps.tags.urls', namespace='tags')),
    url(r'^feedback/', include('backcap.urls')),
    url(r'^ajax/search$', apps.i4p_base.ajax.globalsearch_autocomplete, name='i4p-globalsearch-complete'),
    url(r'^%s/' % settings.ASKBOT_URL , include('apps.forum.urls')),

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

    # Wiki
    (r'^notify/', get_notify_pattern()),
    (r'^wiki/', get_wiki_pattern()),
                             
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
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
     (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^tinymce/', include('tinymce.urls')),
    (r'^uploadify/', include('uploadify.urls')),
                        
    ('^activity/', include('actstream.urls')),

    url(r'autocomplete/', include('autocomplete_light.urls')),

    url('^robots\.txt$', include('robots.urls')),
                        
    url(r'^admin/filebrowser/', include(site.urls)),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^api/', include('apps.api.urls'))
)

## CMS
urlpatterns += i18n_patterns('',
                        url(r'^', include('cms.urls'))
                        )
