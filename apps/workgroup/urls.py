#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
#     url(r'^$', views.GroupListView.as_view(), name='workgroup-list'),
     url(r'^create$', views.GroupCreateView.as_view(), name='workgroup-create'),
                       
     url(r'^(?P<slug>[-\w]+)/$', views.GroupDetailView.as_view(), name='workgroup-detail'),
     url(r'^(?P<slug>[-\w]+)/members$', views.GroupMembersView.as_view(), name='workgroup-members'),
     url(r'^(?P<slug>[-\w]+)/edit/$', views.GroupEditView.as_view(), name='workgroup-edit'),

    # Subscriptions
     url(r'^(?P<workgroup_slug>[-\w]+)/subscribe/$', views.SubscribeView.as_view(), name='workgroup-subscribe'),
     url(r'^(?P<workgroup_slug>[-\w]+)/unsubscribe/$', views.UnsubscribeView.as_view(), name='workgroup-unsubscribe'),
                       
    # Wiki
     url(r'^(?P<workgroup_slug>[-\w]+)/wiki/edit$', views.GroupWikiEdit.as_view(), name='workgroup-wiki-edit'), 
     
     # Group discussion
     url(
         (r'^(?P<workgroup_slug>[-\w]+)/discuss' +
            r'(%s)?' % r'/scope:(?P<scope>\w+)' +
            r'(%s)?' % r'/sort:(?P<sort>[\w\-]+)' +
            r'(%s)?' % r'/query:(?P<query>[^/]+)' +  
            r'(%s)?' % r'/tags:(?P<tags>[\w+.#,-]+)' + 
            r'(%s)?' % r'/author:(?P<author>\d+)' +
            r'(%s)?' % r'/page:(?P<page>\d+)' +
         r'/$'),
         views.GroupDiscussionListView.as_view(),
         name='workgroup-discussion'),
    
    url(r'^(?P<workgroup_slug>[-\w]+)/discuss/open/$', 
            views.GroupDiscussionCreateView.as_view(), 
            name='workgroup-discussion-open'),
                       
    url(r'(?P<workgroup_slug>[-\w]+)/discuss/(?P<question_id>\d+)/', 
            views.GroupDiscussionThreadView.as_view(), 
            name='workgroup-discussion-view'),
    url(r'(?P<workgroup_slug>[-\w]+)/discuss/edit/(?P<question_id>\d+)/', 
            views.GroupDiscussionCreateView.as_view(), 
            name='workgroup-discussion-edit'),
    url(r'(?P<workgroup_slug>[-\w]+)/discuss/answer/(?P<question_id>\d+)/', 
            views.GroupDiscussionNewAnswerView.as_view(),
            name='workgroup-discussion-answer'),
    
)
     
     





