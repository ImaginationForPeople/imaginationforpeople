#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import cache_page
from django.views.generic.simple import direct_to_template

from . import views
from . import ajax

import feeds

PROJECT_AUTHORIZED_FIELDS = "|".join([
    'title',
    'baseline',
    'about_section',
    'partners_section',
    'callto_section',
])

urlpatterns = patterns('',
    url(r'^add/$', views.ProjectTopicSelectView.as_view(), name='project_sheet-start'),
    url(r'^add/(?P<topic_slug>[-\w]+)/$', views.ProjectStartView.as_view(), name='project_sheet-start'),
    url(r'^list/$', views.project_sheet_list, name='project_sheet-list'),
    url(r'^recent-changes/$', views.ProjectRecentChangesView.as_view(), name='project_sheet-recent-changes'),

    url(r'^edit/(?P<topic_slug>[-\w]+)/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, views.project_sheet_edit_field, name='project_sheet-edit-field'),
    url(r'^(?P<slug>[-\w]+)/edit/location/$', views.project_sheet_edit_location, name='project_sheet-instance-edit-location'),
    url(r'^(?P<slug>[-\w]+)/edit/status/$', ajax.project_sheet_edit_status, name='project_sheet-instance-edit-status'),
    url(r'^(?P<slug>[-\w]+)/edit/question/(?P<question_id>[\d]+)/$', views.project_sheet_edit_question, name='project_sheet-instance-edit-question'),
    url(r'^(?P<slug>[-\w]+)/edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, views.project_sheet_edit_field, name='project_sheet-instance-edit-field'),


    url(r'^(?P<project_slug>[-\w]+)/edit/references/$', views.project_sheet_edit_references, name='project_sheet-instance-edit-references'),

    url(r'^(?P<project_slug>[-\w]+)/translate/$', views.project_sheet_create_translation, name='project_sheet-translate'),

    url(r'^(?P<project_slug>[-\w]+)/edit/related/$', views.project_sheet_edit_related, name='project_sheet-instance-edit-related'),
    #AJAX
    url(r'^(?P<project_slug>[-\w]+)/update/related/$', ajax.project_update_related, name='project_sheet-project_update_related'),
    
    url(r'^(?P<project_slug>[-\w]+)/history/$', views.project_sheet_history, name='project_sheet-history'),

    url(r'^(?P<slug>[-\w]+)/$', views.project_sheet_show, name='project_sheet-show'),
    url(r'^(?P<slug>[-\w]+)/add/media/$', views.project_sheet_show, {'add_media' : True}, name='project_sheet-instance-add-media'),

    url(r'^add/media/$', views.project_sheet_add_media, name='project_sheet-add-media'),

    url(r'^add/picture/$', views.project_sheet_add_picture, name='project_sheet-add-picture'),
    url(r'^(?P<slug>[-\w]+)/add/picture/$', views.project_sheet_add_picture, name='project_sheet-instance-add-picture'),
    url(r'^add/video/$', views.project_sheet_add_video, name='project_sheet-add-video'),
    url(r'^(?P<slug>[-\w]+)/add/video/$', views.project_sheet_add_video, name='project_sheet-instance-add-video'),

    url(r'^(?P<slug>[-\w]+)/del/picture/(?P<pic_id>\d+)/$', views.project_sheet_del_picture, name='project_sheet-instance-del-picture'),
    url(r'^(?P<slug>[-\w]+)/del/video/(?P<vid_id>\d+)/$', views.project_sheet_del_video, name='project_sheet-instance-del-video'),

    url(r'^(?P<project_slug>[-\w]+)/member/delete/(?P<username>[-\w]+)/$', views.project_sheet_member_delete, name='project_sheet-instance-del-member'),
    url(r'^(?P<project_slug>[-\w]+)/member/add/$', views.project_sheet_member_add, name='project_sheet-instance-add-member'),

    # Ajax views
    url(r'^start/ajax/field/save/$', ajax.project_textfield_save, name='project_sheet-ajax-field-save'),
    url(r'^start/ajax/field/load/$', ajax.project_textfield_load, name='project_sheet-ajax-field-load'),
    url(r'^(?P<project_slug>[-\w]+)/ajax/field/load/$', ajax.project_textfield_load, name='project_sheet-ajax-field-load'),
    url(r'^(?P<project_slug>[-\w]+)/ajax/field/save/$', ajax.project_textfield_save, name='project_sheet-ajax-field-save'),

    # RSS Feeds
    url(r'^list/new-projects\.rss$', feeds.NewProjectsFeed(), name='project_sheet-new-projects-rss'),
    url(r'^recent-changes\.rss$', feeds.LatestChangesFeed(), name='project_sheet-recent-changes-rss'),

)
