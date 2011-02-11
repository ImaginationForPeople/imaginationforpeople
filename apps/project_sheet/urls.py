from django.conf.urls.defaults import *

from .views import project_sheet_show , project_sheet_edit_field
from django.views.generic.simple import direct_to_template

PROJECT_AUTHORIZED_FIELD = "|".join([
    'title',
    'baseline',
    'about_section',
    'uniqueness_section',
    'value_section',
    'scalability_section'
])

urlpatterns = patterns('',
    url(r'^start/$', direct_to_template, {'template' : 'project_sheet.html'}, name='project_sheet-start'),

    url(r'^edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELD, project_sheet_edit_field, name='project_sheet-edit-field'),
    url(r'^(?P<slug>[-\w]+)/edit/(?P<field>(%s))/$' % PROJECT_AUTHORIZED_FIELD, project_sheet_edit_field, name='project_sheet-instance-edit-field'),
   
    url(r'^(?P<slug>[-\w]+)/$', project_sheet_show, name='project_sheet-show'),
)
