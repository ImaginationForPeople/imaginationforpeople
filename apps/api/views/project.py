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
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.exceptions import ApiFieldError
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from tastypie.throttle import CacheDBThrottle

from apps.i4p_base.models import Location
from apps.project_sheet.models import Answer, I4pProject, I4pProjectTranslation, Topic,\
    ProjectPicture, ProjectReference, ProjectVideo, Site, SiteTopic
from apps.project_sheet.utils import get_project_translations_from_parents
from settings import LANGUAGES

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
        
    def full_dehydrate(self, bundle, for_list=False):
        if len(bundle.obj.all()) > 0:
            bundle.obj = bundle.obj.all()[0] or None
        return ModelResource.full_dehydrate(self, bundle, for_list=for_list)

class LocationDetailResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        include_resource_uri = False
        fields = ['address', 'country']
        
    def full_dehydrate(self, bundle, for_list=False):
        if len(bundle.obj.all()) > 0:
            bundle.obj = bundle.obj.all()[0]
        return ModelResource.full_dehydrate(self, bundle, for_list=for_list)
        
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
    location = fields.ForeignKey(LocationListResource, 'locations', full=True, null=True)
    pictures = fields.ToManyField(ProjectPictureListResource, full=True, null=True, attribute=lambda bundle: ProjectPicture.objects.filter(project=bundle.obj)[:1])
    
    class Meta:
        queryset = I4pProject.objects.all()
        include_resource_uri = False
        fields = [ 'best_of','status' ]

class I4pProjectDetailResource(ModelResource):
    location = fields.ForeignKey(LocationDetailResource, 'locations', full=True, null=True)
    members = fields.ToManyField(UserResource, 'members', full=True)
    objectives = fields.ListField()
    pictures = fields.ToManyField(ProjectPictureDetailResource, 'pictures', full=True, null=True)
    questions = fields.ListField()
    references = fields.ManyToManyField(ProjectReferenceDetailResource, 'references', full=True, null=True)
    videos = fields.ToManyField(ProjectVideoDetailResource, 'videos', full=True, null=True)
    
    class Meta:
        queryset = I4pProject.objects.all()
        include_resource_uri = False
        fields = ['best_of','status', 'website']
        
    def dehydrate_objectives(self, bundle):
        objectives = bundle.obj.objectives.language(translation.get_language()).all()
        return [{"name": objective.name} for objective in objectives]
        
    def dehydrate_questions(self, bundle):
        questions = []
        for topic in Topic.objects.language(translation.get_language()).filter(site_topics=bundle.obj.topics.all()):
            for question in topic.questions.language(translation.get_language()).all().order_by('weight'):
                answers = Answer.objects.language(translation.get_language()).filter(project=bundle.obj.id, question=question)
                questions.append({
                    "question": question.content,
                    "answer": answers and answers[0].content or None
                })
                
        return questions

class I4pProjectTranslationResource(ModelResource):
    project = fields.ForeignKey(I4pProjectDetailResource, use_in='detail', attribute='master', full=True)
    about_section = fields.CharField('about_section', use_in='detail', null=True)
    callto_section = fields.CharField('callto_section', use_in='detail', null=True)
    partners_section = fields.CharField('partners_section', use_in='detail', null=True)
    themes = fields.CharField('themes', use_in='detail', null=True)
    
    class Meta:
        queryset = I4pProjectTranslation.objects.filter(master__in=I4pProject.on_site.all())
        resource_name = 'project'
        throttle = CacheDBThrottle()
        
        bestof_allowed_methods = ['get']
        latest_allowed_methods = ['get']
        random_allowed_methods = ['get']
        bycountry_allowed_methods = ['get']
        fields = ['id', 'slug','language_code','title','baseline']
        filtering = {'language_code' : ['exact']}
        
    def dispatch_detail(self, request, **kwargs):
        if "language_code" in kwargs:
            translation.activate(kwargs["language_code"])
        return ModelResource.dispatch_detail(self, request, **kwargs)
    
    def dispatch_bestof(self, request, **kwargs):
        return self.dispatch('bestof', request, **kwargs)
        
    def dispatch_latest(self, request, **kwargs):
        return self.dispatch('latest', request, **kwargs)
    
    def dispatch_random(self, request, **kwargs):
        return self.dispatch('random', request, **kwargs)
    
    def dispatch_bycountry(self, request, **kwargs):
        return self.dispatch('bycountry', request, **kwargs)
    
    def prepend_urls(self):
        array = []
        array.append(url(r"^(?P<resource_name>%s)/(?P<language_code>[\w]+)/(?P<slug>[\w\d_.-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"))
        array.append(url(r"^(?P<resource_name>%s)/bestof%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_bestof'), name="api_dispatch_bestof"))
        array.append(url(r"^(?P<resource_name>%s)/latest%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_latest'), name="api_dispatch_latest"))
        array.append(url(r"^(?P<resource_name>%s)/random%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_random'), name="api_dispatch_random"))
        array.append(url(r"^(?P<resource_name>%s)/by-country/(?P<country_code>[\w]+)%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_bycountry'), name="api_dispatch_bycountry"))
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
        best_projects = I4pProject.on_site.filter(best_of=True).order_by('?')[:80]
        return self.get_custom(request, best_projects, **kwargs);
    
    def get_latest(self, request, **kwargs):
        latest_projects = I4pProject.on_site.order_by('-created')[:40]
        return self.get_custom(request, latest_projects, **kwargs)
    
    def get_random(self, request, **kwargs):
        self.define_language_code(request)
        
        random_project = I4pProjectTranslation.objects.filter(language_code=self.language_code, master__in=I4pProject.on_site.all()).order_by('?')[0]
        bundle = self.build_bundle(obj=random_project, request=request)
        to_be_serialized = self.full_dehydrate(bundle, for_list=False)
        to_be_serialized = self.alter_detail_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)
    
    def get_bycountry(self, request, **kwargs):
        limit = int(request.GET.get('limit', 50))
        if limit > 50:
            limit = 50
        
        found_projects = I4pProject.on_site.filter(locations__country__icontains=kwargs["country_code"]).order_by('?')[:limit]
        return self.get_custom(request, found_projects, **kwargs)
    
    def full_dehydrate(self, bundle, for_list=False):
        bundle = ModelResource.full_dehydrate(self, bundle, for_list=for_list)
        bundle.related_obj = self
        if for_list is True:
            fk = fields.ForeignKey(I4pProjectListResource, attribute='master', full=True)
            bundle.data['project'] = fk.dehydrate(bundle)
        return bundle

class I4pProjectTranslationListResource(ModelResource):
    """
    Resource used to list I4pProjectTranslation when called from another resource (using ToManyField for example)
    This resource is NOT used to display I4pProjectTranslation as a front end (like using /project/bestof).
    The classic I4pProjectTranslationResource is used for these cases.
    """
    project = fields.ForeignKey(I4pProjectListResource, attribute='master', full=True)
    
    class Meta:
        queryset = I4pProjectTranslation.objects.filter(master__in=I4pProject.on_site.all())
        include_resource_uri = True
        throttle = CacheDBThrottle()
        
        fields = ['slug','language_code','title','baseline']
        
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = ModelResource.detail_uri_kwargs(self, bundle_or_obj)
        kwargs["resource_name"] = I4pProjectTranslationResource.Meta.resource_name
        return kwargs
    
class I4pProjectEditResource(ModelResource):
    """
    Resource used when we have to make edit in database (create, update…) a project sheet
    """
    lang = fields.CharField(null = False)
    # We HAVE TO define site as a field, to avoid error with translations
    # as m2m require an access to created object to save relations
    site = fields.ApiField(null = True)
    topics = fields.ApiField(null = True)
    
    class Meta:
        queryset = I4pProject.objects.all()
        fields = [ "created", "website", "status" ]
        include_resource_uri = False
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        throttle = CacheDBThrottle()
        
        new_allowed_methods = ['post']
        
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        
        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.obj.language_code + "/" + bundle_or_obj.obj.slug
        else:
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.language_code + "/" + bundle_or_obj.slug
            
        return kwargs
        
    def resource_uri_kwargs(self, bundle_or_obj=None):
        kwargs = {
            'resource_name': 'project',
        }
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
            
        if bundle_or_obj is not None:
            kwargs.update(self.detail_uri_kwargs(bundle_or_obj))
            
        return kwargs
        
    def prepend_urls(self):
        array = []
        array.append(url(r"^project/new%s" % trailing_slash(), self.wrap_view('dispatch_new'), name="api_dispatch_new"))
        return array
    
    def dispatch_new(self, request, **kwargs):
        return self.dispatch('new', request, **kwargs)
        
    def post_new(self, request, **kwargs):
        return self.post_list(request, **kwargs)
    
    # This method is used only to check if everything is ok before saving anything
    def alter_deserialized_detail_data(self, request, deserialized):
        # 'Topics' tests
        site = Site.objects.get_current()
        if "topics" not in deserialized or len(deserialized["topics"]) == 0:
            site_topics = SiteTopic.objects.filter(site=site)
            if len(site_topics) > 1:
                raise ApiFieldError("There is more than one topic for this site, you have to provide a 'topics' field");
        else:
            valid_topic = 0
            for topic_slug in deserialized["topics"]:
                site_topic = SiteTopic.objects.filter(site=site, topic__slug=topic_slug) or None
                if site_topic:
                    valid_topic += 1
            if valid_topic == 0:
                raise ApiFieldError("No valid topic provided. Please check your 'topics' field.")
            
        # 'Lang' tests
        if "lang" not in deserialized:
            raise ApiFieldError("The 'lang' parameter is mandatory to create a new project'")
        elif len(deserialized["lang"]) < 1:
            raise ApiFieldError("The 'lang' paramater requires at least one translation")
        else:
            valid_lang = 0
            for language_code, language_data in deserialized['lang'].iteritems():
                if language_code not in dict(LANGUAGES):
                    continue
                if "title" not in language_data:
                    raise ApiFieldError("A translation requires a least a 'title' parameter")
                else:
                    valid_lang += 1 
            if valid_lang == 0:
                raise ApiFieldError("No valid translation sent")
        
        return deserialized
    
    # Read warning above about "site" field
    def hydrate_site(self, bundle):
        bundle.obj.site.add(Site.objects.get_current())
        return bundle
    
    def hydrate_topics(self, bundle):
        site = Site.objects.get_current()
        if "topics" not in bundle.data or len(bundle.data["topics"]) == 0:
            site_topics = SiteTopic.objects.filter(site=site)
            bundle.obj.topics.add(site_topics[0])
        else:
            for topic_slug in bundle.data["topics"]:
                site_topic = SiteTopic.objects.filter(site=site, topic__slug=topic_slug) or None
                if site_topic:
                    bundle.obj.topics.add(site_topic[0])
            
        return bundle
    
    def hydrate_lang(self, bundle):
        translated_bundle = Bundle()
        translation_resource = I4pProjectTranslationEditResource()
        
        for language_code, language_data in bundle.data['lang'].iteritems():
            if language_code not in dict(LANGUAGES):
                continue
            translated_bundle.data = language_data
            translated_bundle.obj = bundle.obj.translate(language_code)
            translation_resource.obj_create(translated_bundle)
            
        return bundle

class I4pProjectTranslationEditResource(ModelResource):
    """
    Internal resource to create translations with API POST
    """
    innovation_section = fields.CharField(attribute = "innovation_section", null = True)
    about_section = fields.CharField(attribute = "about_section", null = True)
    baseline = fields.CharField(attribute = "baseline", null = True)
    title = fields.CharField(attribute = "title")
    themes = fields.CharField(attribute = "themes", null = True)
    class Meta:
        queryset = I4pProject.objects.all()
        
    def obj_create(self, bundle, **kwargs):
        bundle = self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle
