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

from django.conf.urls import url

from easy_thumbnails.files import get_thumbnailer
from tagging.models import Tag
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from tastypie.throttle import CacheDBThrottle
from wiki.models.article import Article, ArticleForObject

from apps.project_sheet.project_pictures_specs import ResizeThumbApi,ResizeDisplay
from apps.project_sheet.models import I4pProjectTranslation
from apps.workgroup.models import WorkGroup

from .project import I4pProjectTranslationListResource, UserResource

class WorkgroupResource(ModelResource):
    """
    Resource used to display WorkGroup model using the API
    """
    subscribers = fields.ToManyField(UserResource, "subscribers", use_in="detail", full=True, null=True)
    projects = fields.ToManyField(I4pProjectTranslationListResource, use_in="detail", full=True, null=True, attribute=lambda bundle:I4pProjectTranslation.objects.filter(master__in=bundle.obj.projects.all(), language_code=bundle.obj.language))
    description = fields.CharField('description', use_in='detail', null=True)
    
    class Meta:
        queryset = WorkGroup.objects.all()
        resource_name = "workgroup"
        throttle = CacheDBThrottle()
        fields = ["name", "language", "slug"]
        filtering = {
            "language": 'exact',
        }
    
    def prepend_urls(self):
        array = []
        array.append(url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"))
        return array
        
    def full_dehydrate(self, bundle, for_list=False):
        bundle = ModelResource.full_dehydrate(self, bundle, for_list)
        if bundle.obj.picture:
            thumbnailer = get_thumbnailer(bundle.obj.picture)
            thumbnail_options = {'size': (ResizeThumbApi.width, ResizeThumbApi.height)}
            bundle.data["thumb"] = thumbnailer.get_thumbnail(thumbnail_options).url
        else:
            bundle.data["thumb"] = None
        if for_list is False:
            bundle.data["tags"] = [tag.name for tag in Tag.objects.get_for_object(bundle.obj)]
            if(bundle.obj.picture):
                thumbnail_options = {'size': (ResizeDisplay.width, ResizeDisplay.width)}
                bundle.data["image"] = thumbnailer.get_thumbnail(thumbnail_options).url
            else:
                bundle.data["image"] = None
            try:
                bundle.data["article"] = Article.get_for_object(bundle.obj).render()
            except ArticleForObject.DoesNotExist:
                bundle.data["article"] = None
        return bundle
