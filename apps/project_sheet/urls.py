from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from .views import project_sheet_show , project_sheet_edit_field, project_sheet_edit_themes, project_sheet_add_picture

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

    url(r'^(?P<project_slug>[-\w]+)/edit/themes/$', project_sheet_edit_themes, name='project_sheet-instance-edit-themes'),
   
    url(r'^(?P<slug>[-\w]+)/$', project_sheet_show, name='project_sheet-show'),

    url(r'^add/picture/$', project_sheet_add_picture, name='project_sheet-add-picture'),
    url(r'^(?P<slug>[-\w]+)/add/picture/$', project_sheet_add_picture, name='project_sheet-instance-add-picture'),
)
