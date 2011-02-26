from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from .views import project_sheet_show, project_sheet_edit_field, project_sheet_edit_related
from .views import project_sheet_add_picture, project_sheet_add_video, project_sheet_add_media, project_sheet_create_translation

PROJECT_AUTHORIZED_FIELDS = "|".join([
    'title',
    'baseline',
    'about_section',
    'uniqueness_section',
    'value_section',
    'scalability_section'
])

urlpatterns = patterns('',
    url(r'^start/$', direct_to_template, {'template' : 'project_sheet.html'}, name='project_sheet-start'),

    url(r'^edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, project_sheet_edit_field, name='project_sheet-edit-field'),
    url(r'^(?P<slug>[-\w]+)/edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELDS, project_sheet_edit_field, name='project_sheet-instance-edit-field'),

    url(r'^(?P<project_slug>[-\w]+)/translate$', project_sheet_create_translation, name='project_sheet-translate'),

    url(r'^(?P<project_slug>[-\w]+)/edit/related/$', project_sheet_edit_related, name='project_sheet-instance-edit-related'),
   
    url(r'^(?P<slug>[-\w]+)/$', project_sheet_show, name='project_sheet-show'),
    
    url(r'^add/media/$', project_sheet_add_media, name='project_sheet-add-media'),
    url(r'^(?P<slug>[-\w]+)/add/media/$', project_sheet_add_media, name='project_sheet-instance-add-media'),
    url(r'^add/picture/$', project_sheet_add_picture, name='project_sheet-add-picture'),
    url(r'^(?P<slug>[-\w]+)/add/picture/$', project_sheet_add_picture, name='project_sheet-instance-add-picture'),
    url(r'^add/video/$', project_sheet_add_video, name='project_sheet-add-video'),
    url(r'^(?P<slug>[-\w]+)/add/video/$', project_sheet_add_video, name='project_sheet-instance-add-video'),
)
