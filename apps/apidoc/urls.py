#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
     url(r'^project/', views.I4pProjectApiHelp.as_view())
)
