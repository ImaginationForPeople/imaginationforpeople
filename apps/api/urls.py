#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url, include

from tastypie.api import Api

from .views.project import I4pProjectTranslationResource

v1_api = Api(api_name="v1")
v1_api.register(I4pProjectTranslationResource())

urlpatterns = patterns('',
     url(r'^', include(v1_api.urls)),
)
