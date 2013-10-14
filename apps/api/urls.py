#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url, include

from tastypie.api import Api

from .views.project import I4pProjectTranslationResource, I4pProjectEditResource
from .views.search import SearchResource
from .views.workgroup import WorkgroupResource
from .views.picture import ProjectPictureResource

v1_api = Api(api_name="v1")
v1_api.register(I4pProjectTranslationResource())
v1_api.register(SearchResource())
v1_api.register(WorkgroupResource())
v1_api.register(ProjectPictureResource())
v1_api.register(I4pProjectEditResource())

urlpatterns = patterns('',
     url(r'^', include(v1_api.urls)),
)
