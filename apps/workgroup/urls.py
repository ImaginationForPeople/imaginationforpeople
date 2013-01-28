#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
#     url(r'^$', views.GroupListView.as_view(), name='workgroup-list'),
     url(r'^create$', views.GroupCreateView.as_view(), name='workgroup-create'),
                       
     url(r'^(?P<slug>[-\w]+)/$', views.GroupDetailView.as_view(), name='workgroup-detail'),
     url(r'^(?P<slug>[-\w]+)/edit/$', views.GroupEditView.as_view(), name='workgroup-edit'),

    # Subscriptions
     url(r'^(?P<workgroup_slug>[-\w]+)/subscribe/$', views.SubscribeView.as_view(), name='workgroup-subscribe'),
     url(r'^(?P<workgroup_slug>[-\w]+)/unsubscribe/$', views.UnsubscribeView.as_view(), name='workgroup-unsubscribe'),
                       
    # Wiki
     url(r'^(?P<workgroup_slug>[-\w]+)/wiki/edit$', views.GroupWikiEdit.as_view(), name='workgroup-wiki-edit'),                                                                     
)





