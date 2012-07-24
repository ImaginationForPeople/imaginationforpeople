#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

from piston.resource import Resource

from apps.api.viewproject import I4pProjectTranslationHandler

urlpatterns = patterns('',
     url(r'^viewproject/(?P<project_id>[\d]+)$', Resource(I4pProjectTranslationHandler)),
)
