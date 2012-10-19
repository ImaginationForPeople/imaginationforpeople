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
from django.contrib.auth.models import User
from django.utils import translation

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash

from apps.i4p_base.models import Location
from apps.project_sheet.models import Answer, Objective, I4pProject, I4pProjectTranslation, Topic,\
    ProjectPicture, ProjectReference, ProjectVideo
from apps.project_sheet.utils import get_project_translations_from_parents

class ProjectReferenceDetailResource(ModelResource):
    class Meta:
        queryset = ProjectReference.objects.all()
        include_resource_uri = False
        fields = ['desc']

class LocationListResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        include_resource_uri = False
        fields = ['country']

class LocationDetailResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        include_resource_uri = False
        fields = ['address', 'country']
        
class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        include_resource_uri = False
        fields = ['username']
    
    def dehydrate(self, bundle):
        bundle.data['fullname'] = bundle.obj.get_full_name()
        bundle.data['avatar'] = bundle.obj.get_profile().get_mugshot_url()
        return bundle

class ProjectVideoDetailResource(ModelResource):
    class Meta:
        queryset = ProjectVideo.objects.all()
        include_resource_uri = False
        fields = ["video_url"]
        
class ProjectPictureListResource(ModelResource):
    class Meta:
        queryset = ProjectPicture.objects.all()
        include_resource_uri = False
        fields = [None]
    
    def dehydrate(self, bundle):
        bundle.data['thumb'] = bundle.obj.thumbnail_api.url
        return bundle
    
class ProjectPictureDetailResource(ModelResource):
    class Meta:
        queryset = ProjectPicture.objects.all()
        include_resource_uri = False
        fields = ['author', 'created', 'desc', 'license', 'source']
    
    def dehydrate(self, bundle):
        bundle.data['thumb'] = bundle.obj.thumbnail_api.url
        bundle.data['url'] = bundle.obj.display_api.url
        return bundle
    
class I4pProjectListResource(ModelResource):
    location = fields.ForeignKey(LocationListResource, 'location', full=True, null=True)
    pictures = fields.ToManyField(ProjectPictureListResource, 'pictures', full=True, null=True)
    
    class Meta:
        queryset = I4pProject.objects.all()
        include_resource_uri = False
        fields = ['best_of','status']

class I4pProjectDetailResource(ModelResource):
    location = fields.ForeignKey(LocationDetailResource, 'location', full=True, null=True)
    members = fields.ToManyField(UserResource, 'members', full=True)
    pictures = fields.ToManyField(ProjectPictureDetailResource, 'pictures', full=True, null=True)
    videos = fields.ToManyField(ProjectVideoDetailResource, 'videos', full=True, null=True)
    references = fields.ManyToManyField(ProjectReferenceDetailResource, 'references', full=True, null=True)
    
    class Meta:
        queryset = I4pProject.objects.all()
        include_resource_uri = False
        fields = ['best_of','status', 'website']
        
    def dehydrate(self, bundle):
        objectives = bundle.obj.objectives.language(translation.get_language()).all()
        bundle.data['objectives'] = [{"name": objective.name} for objective in objectives]
        
        questions = []
        for topic in Topic.objects.language(translation.get_language()).filter(site_topics=bundle.obj.topics.all()):
            for question in topic.questions.language(translation.get_language()).all().order_by('weight'):
                answers = Answer.objects.language(translation.get_language()).filter(project=bundle.obj.id, question=question)
                questions.append({
                    "question": question.content,
                    "answer": answers and answers[0].content or None
                })
                
        bundle.data['questions'] = questions
        return bundle

class I4pProjectTranslationResource(ModelResource):
    project = fields.ForeignKey(I4pProjectDetailResource, use_in='detail', attribute='project', full=True)
    about_section = fields.CharField('about_section', use_in='detail', null=True)
    callto_section = fields.CharField('callto_section', use_in='detail', null=True)
    partners_section = fields.CharField('partners_section', use_in='detail', null=True)
    themes = fields.CharField('themes', use_in='detail', null=True)
    
    class Meta:
        queryset = I4pProjectTranslation.objects.all()
        resource_name = 'project'
        
        bestof_allowed_methods = ['get']
        latest_allowed_methods = ['get']
        random_allowed_methods = ['get']
        fields = ['id', 'slug','language_code','title','baseline']
        
    def dispatch_detail(self, request, **kwargs):
        translation.activate(kwargs["language_code"])
        return ModelResource.dispatch_detail(self, request, **kwargs)
    
    def dispatch_bestof(self, request, **kwargs):
        return self.dispatch('bestof', request, **kwargs)
        
    def dispatch_latest(self, request, **kwargs):
        return self.dispatch('latest', request, **kwargs)
    
    def dispatch_random(self, request, **kwargs):
        return self.dispatch('random', request, **kwargs)
    
    def prepend_urls(self):
        array = []
        array.append(url(r"^(?P<resource_name>%s)/(?P<language_code>[\w]+)/(?P<slug>[\w\d_.-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"))
        array.append(url(r"^(?P<resource_name>%s)/bestof%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_bestof'), name="api_dispatch_bestof"))
        array.append(url(r"^(?P<resource_name>%s)/latest%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_latest'), name="api_dispatch_latest"))
        array.append(url(r"^(?P<resource_name>%s)/random%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_random'), name="api_dispatch_random"))
        return array
    
    def define_language_code(self, request):
        self.language_code = request.GET.get('lang', 'en')
        if self.language_code not in dict(settings.LANGUAGES) :
                self.language_code = "en"
        
        translation.activate(self.language_code)
    
    def get_custom(self, request, projects, **kwargs):
        self.define_language_code(request)
        
        localized_latest_projects = get_project_translations_from_parents(projects, self.language_code, "en", True)
        bundles = [self.build_bundle(obj=obj, request=request) for obj in localized_latest_projects]
        to_be_serialized = [self.full_dehydrate(bundle, for_list=True) for bundle in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)
    
    def get_bestof(self, request, **kwargs):
        best_projects = I4pProject.objects.filter(best_of=True).order_by('?')[:80]
        return self.get_custom(request, best_projects, **kwargs);
    
    def get_latest(self, request, **kwargs):
        latest_projects = I4pProject.objects.order_by('-created')[:40]
        return self.get_custom(request, latest_projects, **kwargs)
    
    def get_random(self, request, **kwargs):
        self.define_language_code(request)
        
        random_project = I4pProjectTranslation.objects.filter(language_code=self.language_code).order_by('?')[0]
        bundle = self.build_bundle(obj=random_project, request=request)
        to_be_serialized = self.full_dehydrate(bundle, for_list=False)
        to_be_serialized = self.alter_detail_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)
    
    def full_dehydrate(self, bundle, for_list=False):
        bundle = ModelResource.full_dehydrate(self, bundle, for_list=for_list)
        bundle.related_obj = self
        if for_list is True:
            fk = fields.ForeignKey(I4pProjectListResource, attribute='project', full=True)
            bundle.data['project'] = fk.dehydrate(bundle)
        return bundle
