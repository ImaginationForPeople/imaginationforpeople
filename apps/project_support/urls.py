from django.conf.urls.defaults import patterns, url, include
from . import views

urlpatterns = patterns('',
    url(r'^$', views.ProjectSupportView.as_view(), name='project_support_main'),
)