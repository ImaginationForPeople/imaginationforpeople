#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

from . import views
from apps.project_support import views as support_views
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
    url(r'^list/$', views.ProjectList.as_view(), name='project_sheet-list'),
    url(r'^recent-changes/$', views.ProjectRecentChangesView.as_view(), name='project_sheet-recent-changes'),
    #List all existing supports of all projects
    # url(r'^list-all-supports$',support_views.ProjectSupportListAll.as_view(),name='project_support_list_all'),
    url(# Note that all parameters, even if optional, are provided to the view. Non-present ones have None value.
        (r'^supports' +
            r'(%s)?' % r'/scope:(?P<scope>\w+)' +
            r'(%s)?' % r'/sort:(?P<sort>[\w\-]+)' +
            r'(%s)?' % r'/query:(?P<query>[^/]+)' +  
            r'(%s)?' % r'/tags:(?P<tags>[\w+.#,-]+)' + 
            r'(%s)?' % r'/author:(?P<author>\d+)' +
            r'(%s)?' % r'/page:(?P<page>\d+)' +
        r'/$'),
        
        support_views.ProjectSupportListAll.as_view(),
        name='project_support_list_all'
    ),
    
    # Show
    url(r'^(?P<slug>[-\w]+)/$', views.ProjectView.as_view(), name='project_sheet-show'),

    # Edits
    url(r'^edit/(?P<topic_slug>[-\w]+)/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, views.project_sheet_edit_field, name='project_sheet-edit-field'),
    url(r'^(?P<slug>[-\w]+)/edit/tags/$', views.ProjectEditTagsView.as_view(), name='project_sheet-instance-edit-tags'),                       
    url(r'^(?P<slug>[-\w]+)/edit/info/$', views.ProjectEditInfoView.as_view(), name='project_sheet-instance-edit-info'),
    url(r'^(?P<slug>[-\w]+)/edit/status/$', ajax.project_sheet_edit_status, name='project_sheet-instance-edit-status'),
    url(r'^(?P<slug>[-\w]+)/edit/question/(?P<question_id>[\d]+)/$', views.project_sheet_edit_question, name='project_sheet-instance-edit-question'),
    url(r'^(?P<slug>[-\w]+)/edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, views.project_sheet_edit_field, name='project_sheet-instance-edit-field'),

    # References
    url(r'^(?P<slug>[-\w]+)/edit/references/$', views.ProjectEditReferencesView.as_view(), name='project_sheet-instance-edit-references'),

    # History
    url(r'^(?P<slug>[-\w]+)/history/$', views.ProjectHistoryView.as_view(), name='project_sheet-instance-history'),
                       
    # Media
    url(r'^(?P<slug>[-\w]+)/gallery/$', views.ProjectGalleryView.as_view(), name='project_sheet-instance-gallery'),
    url(r'^(?P<slug>[-\w]+)/gallery/picture/add/$', views.ProjectGalleryAddPictureView.as_view(), name='project_sheet-instance-picture-add'),
    url(r'^(?P<slug>[-\w]+)/gallery/picture/(?P<pic_id>\d+)/del/$', views.project_sheet_del_picture, name='project_sheet-instance-picture-del'),                       
    # url(r'^add/media/$', views.project_sheet_add_media, name='project_sheet-add-media'),
    # url(r'^add/picture/$', views.project_sheet_add_picture, name='project_sheet-add-picture'),
    # url(r'^add/video/$', views.project_sheet_add_video, name='project_sheet-add-video'),
    url(r'^(?P<slug>[-\w]+)/gallery/video/add/$', views.ProjectGalleryAddVideoView.as_view(), name='project_sheet-instance-video-add'),
    url(r'^(?P<slug>[-\w]+)/gallery/video/(?P<vid_id>\d+)/del/$', views.project_sheet_del_video, name='project_sheet-instance-video-del'),

    # Members
    url(r'^(?P<project_slug>[-\w]+)/member/delete/(?P<username>[-\w]+)/$', views.project_sheet_member_delete, name='project_sheet-instance-del-member'),
    url(r'^(?P<slug>[-\w]+)/member/add/$', views.ProjectMemberAddView.as_view(), name='project_sheet-instance-add-member'),

    # Translations
    url(r'^(?P<project_slug>[-\w]+)/translate/$', views.project_sheet_create_translation, name='project_sheet-translate'),

    # Ajax views
    url(r'^(?P<project_slug>[-\w]+)/update/related/$', ajax.project_update_related, name='project_sheet-project_update_related'),                  
    url(r'^start/ajax/field/save/$', ajax.project_textfield_save, name='project_sheet-ajax-field-save'),
    url(r'^start/ajax/field/load/$', ajax.project_textfield_load, name='project_sheet-ajax-field-load'),
    url(r'^(?P<project_slug>[-\w]+)/ajax/field/load/$', ajax.project_textfield_load, name='project_sheet-ajax-field-load'),
    url(r'^(?P<project_slug>[-\w]+)/ajax/field/save/$', ajax.project_textfield_save, name='project_sheet-ajax-field-save'),

    # RSS Feeds
    url(r'^list/new-projects\.rss$', feeds.NewProjectsFeed(), name='project_sheet-new-projects-rss'),
    url(r'^recent-changes\.rss$', feeds.LatestChangesFeed(), name='project_sheet-recent-changes-rss'),
    
    
    
    # Supports 
    url( #from askbot
        (r'^(?P<project_slug>[-\w]+)/support' +
            r'(%s)?' % r'/scope:(?P<scope>\w+)' +
            r'(%s)?' % r'/sort:(?P<sort>[\w\-]+)' +
            r'(%s)?' % r'/query:(?P<query>[^/]+)' +  
            r'(%s)?' % r'/tags:(?P<tags>[\w+.#,-]+)' + 
            r'(%s)?' % r'/author:(?P<author>\d+)' +
            r'(%s)?' % r'/page:(?P<page>\d+)' +
        r'/$'),

        support_views.ProjectSupportListView.as_view(), 
        name='project_support_main'
    ),
    url(r'^(?P<project_slug>[-\w]+)/support/propose/$', support_views.propose_project_support, name='project_support_propose'),
    url(r'(?P<project_slug>[-\w]+)/support/(?P<question_id>\d+)/', support_views.view_project_support, name='project_support_view'),
    url(r'(?P<project_slug>[-\w]+)/support/edit/(?P<question_id>\d+)/', support_views.propose_project_support, name='project_support_edit'),
    url(r'(?P<project_slug>[-\w]+)/support/answer/(?P<question_id>\d+)/', support_views.answer_project_support, name='project_support_answer'),
    url(r'(?P<project_slug>[-\w]+)/support/answer/edit/(?P<answer_id>\d+)/', support_views.edit_support_answer, name='project_support_edit_answer'),
    
    #Discuss
    url( #from askbot
        (r'^(?P<project_slug>[-\w]+)/discuss' +
            r'(%s)?' % r'/scope:(?P<scope>\w+)' +
            r'(%s)?' % r'/sort:(?P<sort>[\w\-]+)' +
            r'(%s)?' % r'/query:(?P<query>[^/]+)' +  
            r'(%s)?' % r'/tags:(?P<tags>[\w+.#,-]+)' + 
            r'(%s)?' % r'/author:(?P<author>\d+)' +
            r'(%s)?' % r'/page:(?P<page>\d+)' +
        r'/$'),

        views.ProjectDiscussionListView.as_view(), 
        name='project_discussion_list'
    ),
)
