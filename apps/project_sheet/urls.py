#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

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
    # Creating
    url(r'^add/$', views.ProjectTopicSelectView.as_view(), name='project_sheet-start'),
    url(r'^add/(?P<topic_slug>[-\w]+)/$', views.ProjectStartView.as_view(), name='project_sheet-start'),

    # Listing
    url(r'^list/$', views.project_sheet_list, name='project_sheet-list'),
    url(r'^recent-changes/$', views.ProjectRecentChangesView.as_view(), name='project_sheet-recent-changes'),

    # Show
    url(r'^(?P<slug>[-\w]+)/$', views.ProjectView.as_view(), name='project_sheet-show'),

    # Edits
    url(r'^edit/(?P<topic_slug>[-\w]+)/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, views.project_sheet_edit_field, name='project_sheet-edit-field'),
    url(r'^(?P<slug>[-\w]+)/edit/tags/$', views.ProjectEditTagsView.as_view(), name='project_sheet-instance-edit-tags'),                       
    url(r'^(?P<slug>[-\w]+)/edit/location/$', views.ProjectEditLocationView.as_view(), name='project_sheet-instance-edit-location'),
    url(r'^(?P<slug>[-\w]+)/edit/info/$', views.ProjectEditInfoView.as_view(), name='project_sheet-instance-edit-info'),
    url(r'^(?P<slug>[-\w]+)/edit/status/$', ajax.project_sheet_edit_status, name='project_sheet-instance-edit-status'),
    url(r'^(?P<slug>[-\w]+)/edit/question/(?P<question_id>[\d]+)/$', views.project_sheet_edit_question, name='project_sheet-instance-edit-question'),
    url(r'^(?P<slug>[-\w]+)/edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, views.project_sheet_edit_field, name='project_sheet-instance-edit-field'),

    # References
    url(r'^(?P<slug>[-\w]+)/edit/references/$', views.ProjectEditReferencesView.as_view(), name='project_sheet-instance-edit-references'),

    # History
    url(r'^(?P<project_slug>[-\w]+)/history/$', views.project_sheet_history, name='project_sheet-history'),
                       
    # Media
    url(r'^(?P<slug>[-\w]+)/add/media/$', views.ProjectView.as_view(), {'add_media' : True}, name='project_sheet-instance-add-media'),
    url(r'^add/media/$', views.project_sheet_add_media, name='project_sheet-add-media'),
    url(r'^add/picture/$', views.project_sheet_add_picture, name='project_sheet-add-picture'),
    url(r'^(?P<slug>[-\w]+)/add/picture/$', views.project_sheet_add_picture, name='project_sheet-instance-add-picture'),
    url(r'^add/video/$', views.project_sheet_add_video, name='project_sheet-add-video'),
    url(r'^(?P<slug>[-\w]+)/add/video/$', views.project_sheet_add_video, name='project_sheet-instance-add-video'),
    url(r'^(?P<slug>[-\w]+)/del/picture/(?P<pic_id>\d+)/$', views.project_sheet_del_picture, name='project_sheet-instance-del-picture'),
    url(r'^(?P<slug>[-\w]+)/del/video/(?P<vid_id>\d+)/$', views.project_sheet_del_video, name='project_sheet-instance-del-video'),

    # Members
    url(r'^(?P<project_slug>[-\w]+)/member/delete/(?P<username>[-\w]+)/$', views.project_sheet_member_delete, name='project_sheet-instance-del-member'),
    url(r'^(?P<project_slug>[-\w]+)/member/add/$', views.project_sheet_member_add, name='project_sheet-instance-add-member'),

    # Translations
    url(r'^(?P<project_slug>[-\w]+)/translate/$', views.project_sheet_create_translation, name='project_sheet-translate'),

    # Ajax views
    url(r'^(?P<project_slug>[-\w]+)/update/related/$', ajax.project_update_related, name='project_sheet-project_update_related'),                  url(r'^start/ajax/field/save/$', ajax.project_textfield_save, name='project_sheet-ajax-field-save'),
    url(r'^start/ajax/field/load/$', ajax.project_textfield_load, name='project_sheet-ajax-field-load'),
    url(r'^(?P<project_slug>[-\w]+)/ajax/field/load/$', ajax.project_textfield_load, name='project_sheet-ajax-field-load'),
    url(r'^(?P<project_slug>[-\w]+)/ajax/field/save/$', ajax.project_textfield_save, name='project_sheet-ajax-field-save'),

    # RSS Feeds
    url(r'^list/new-projects\.rss$', feeds.NewProjectsFeed(), name='project_sheet-new-projects-rss'),
    url(r'^recent-changes\.rss$', feeds.LatestChangesFeed(), name='project_sheet-recent-changes-rss'),

)
