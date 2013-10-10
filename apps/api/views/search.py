# -*- encoding: utf-8 -*-
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.conf.urls import url
from django.utils import translation

from haystack.query import SearchQuerySet
from tastypie.resources import Resource
from tastypie.utils.urls import trailing_slash
from tastypie.throttle import CacheDBThrottle

from apps.project_sheet.models import I4pProject

class SearchResource(Resource):
    class Meta:
        resource_name = "search"
        include_resource_uri = False
        project_allowed_methods = ['get']
        throttle = CacheDBThrottle()
        
    def prepend_urls(self):
        array = []
        array.append(url(r"^(?P<resource_name>%s)/project%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_project'), name="api_dispatch_search"))
        return array
    
    def dispatch_project(self, request, **kwargs):
        return self.dispatch('project', request, **kwargs)
    
    def get_project(self, request, **kwargs):
        self.language_code = request.GET.get('lang', 'en')
        if self.language_code not in dict(settings.LANGUAGES):
                self.language_code = "en"
        
        translation.activate(self.language_code)
        
        limit = int(request.GET.get('limit', 50))
        if limit > 50:
            limit = 50 
        
        bundles = []
        found_projects = SearchQuerySet().models(I4pProject).filter_and(text__icontains=request.GET['q'], language_codes__icontains=self.language_code, sites=settings.SITE_ID)[:limit]
        for project in found_projects:
            if project.object:
                bundles.append(self.build_bundle(obj=project, data={"language_code": self.language_code, "slug": project.object.slug, "title": project.object.title}, request=request))
        to_be_serialized = [self.full_dehydrate(bundle, for_list=True) for bundle in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)