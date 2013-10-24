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

from licenses.models import License

from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ApiFieldError
from tastypie.resources import ModelResource
from tastypie.throttle import CacheDBThrottle

from apps.project_sheet.models import I4pProject, ProjectPicture
from apps.project_sheet.utils import I4pProjectTranslation

class ProjectPictureResource(ModelResource):
    image = fields.Base64FileField(attribute="original_image")
    project = fields.ApiField()
    license = fields.IntegerField()
    
    class Meta:
        queryset = ProjectPicture.objects.all()
        resource_name = 'picture'
        throttle = CacheDBThrottle()
        
        authentication = ApiKeyAuthentication()
        authorization=Authorization()
        allowed_methods = ['post']
        fields = ["desc", "author", "source"]
    
    
    def hydrate_project(self, bundle):
        if "project" not in bundle.data or "slug" not in bundle.data["project"] or "lang" not in bundle.data["project"]:
            raise ApiFieldError("A picture must be attached to a project")
        
        project = bundle.data["project"]
        try:
            project = I4pProjectTranslation.objects.get(slug=project["slug"], language_code=project["lang"], master__in=I4pProject.on_site.all())
        except:
            raise ApiFieldError("Unable to find associated project")
        
        project = project.master
        bundle.obj.project = project
        return bundle
        
    def hydrate_license(self, bundle):
        if "license" not in bundle.data:
            raise ApiFieldError("You must set a license for your picture")
        
        try:
            license = License.objects.get(id=bundle.data["license"])
        except:
            raise ApiFieldError("The selected license is incorrect")
        
        bundle.obj.license = license
        return bundle
