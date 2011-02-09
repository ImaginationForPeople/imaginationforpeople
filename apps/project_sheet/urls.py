from django.conf.urls.defaults import *
from .views import edit_project_sheet

urlpatterns = patterns('',
    url(r'^create/$', edit_project_sheet, name='project_sheet_edit'),
)