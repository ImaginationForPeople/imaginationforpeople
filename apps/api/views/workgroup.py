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

from tagging.models import Tag
from tastypie import fields 
from tastypie.resources import ModelResource

from apps.workgroup.models import WorkGroup
from apps.project_sheet.models import I4pProjectTranslation

from .project import UserResource, I4pProjectTranslationListResource

class WorkgroupResource(ModelResource):
    subscribers = fields.ToManyField(UserResource, "subscribers", full=True, null=True)
    projects = fields.ToManyField(I4pProjectTranslationListResource, full=True, null=True, attribute=lambda bundle:I4pProjectTranslation.objects.filter(project__in=bundle.obj.projects.all(), language_code=bundle.obj.language))
    
    class Meta:
        queryset = WorkGroup.objects.all()
        resource_name="workgroup"
        fields = ["name", "description", "language"]
        
    def dehydrate(self, bundle):
        bundle.data["tags"] = [tag.name for tag in Tag.objects.get_for_object(bundle.obj)]
        bundle.data["image"] = bundle.obj.picture and bundle.obj.picture.url or None
        return bundle
