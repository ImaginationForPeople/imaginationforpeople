#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

from piston.resource import Resource

from .views.about import AboutHandler
from .views.project import I4pProjectTranslationHandler

urlpatterns = patterns('',
     url(r'^about/', Resource(AboutHandler)),
     url(r'^project/(?P<project_id>[\d]+)$', Resource(I4pProjectTranslationHandler)),
     url(r'^project/$', Resource(I4pProjectTranslationHandler)),
)
