from django.conf import settings
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import translation
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.views.decorators.vary import vary_on_headers

from haystack.query import SearchQuerySet
from serializers import ModelSerializer, Field

from apps.member.models import I4pProfile
from apps.project_sheet.models import I4pProject, I4pProjectTranslation
from apps.project_sheet.utils import get_project_translations_from_parents
from apps.workgroup.models import WorkGroup

def _slider_make_response(request, queryset):
    count = int(request.GET.get('count', 14))
    project_translations = get_project_translations_from_parents(parents_qs=queryset[:count],
                                                                 language_code=request.LANGUAGE_CODE)
    
    return render_to_response(template_name='pages/home-blocks/slider.html',
                              dictionary={'project_translations': project_translations},
                              context_instance=RequestContext(request))
    
@require_GET
@cache_page(60 * 5)
@vary_on_headers('Host')
def slider_bestof(request):
    """
    Get the "count" bestof projects at random
    """
    return _slider_make_response(request,
                                 queryset=I4pProject.on_site.filter(best_of=True).order_by('?'))



@require_GET
@cache_page(60 * 5)
@vary_on_headers('Host')
def slider_latest(request):
    """
    Get the "count" latests projects, sorted by creation time
    """
    return _slider_make_response(request,
                                 queryset=I4pProject.on_site.order_by('-created'))


@require_GET
@cache_page(60 * 5)
@vary_on_headers('Host')
def slider_most_commented(request):
    """
    Get the most commented projects
    """
    count = int(request.GET.get('count', 14))
    site = Site.objects.get_current()
    current_language_code = translation.get_language()
    
    i4pprojecttranslation_type = ContentType.objects.get_for_model(I4pProjectTranslation)
    comment_model = comments.get_model()

    req = comment_model.objects.filter(content_type__pk=i4pprojecttranslation_type.id).values('object_pk').annotate(comment_count=Count('object_pk')).order_by("-comment_count")
    parent_projects = site.projects.filter(id__in=[x['object_pk'] for x in req])
    project_translations = get_project_translations_from_parents(parents_qs=parent_projects,
                                                                 language_code=current_language_code)
    
    return render_to_response(template_name='pages/home-blocks/slider.html',
                              dictionary={'project_translations': project_translations},
                              context_instance=RequestContext(request))


class ProjectSerializer(ModelSerializer):
    """
    A serializer for the I4PProject Models
    """
    class Meta:
        fields = ('title', 'get_absolute_url', 'image')
    get_absolute_url = Field(source='*', convert=lambda obj: obj.get_absolute_url())
    image = Field(source='*', convert=lambda obj: ProjectSerializer.get_mosaic(obj))

    @staticmethod
    def get_mosaic(obj):
        p = obj.project.get_primary_picture()
        if p:
            return p.mosaic_tile.url
        else:
            return settings.STATIC_URL + "images/home/picto-projects.jpg"

class WorkGroupSerializer(ModelSerializer):
    """
    A serializer for the WorkGroup Models
    """
    class Meta:
        fields = ('title', 'get_absolute_url', 'image')
    get_absolute_url = Field(source='*', convert=lambda obj: obj.get_absolute_url())
    image = Field(source='*', convert=lambda obj: WorkGroupSerializer.get_mosaic(obj))

class I4pProfileSerializer(ModelSerializer):
    """
    A serializer for the I4pProfile Models
    """
    class Meta:
        fields = ('title', 'get_absolute_url', 'image')
    get_absolute_url = Field(source='*', convert=lambda obj: obj.get_absolute_url())
    image = Field(source='*', convert=lambda obj: I4pProfileSerializer.get_mosaic(obj))


def globalsearch_autocomplete(request):
    """
    Suggest results while typing in the search bar
    """
    current_language_code = translation.get_language()

    question = request.GET.get('q', '')

    # matches
    matches = SearchQuerySet().models(
        I4pProjectTranslation, I4pProfile, WorkGroup
    ).filter(
        language_code=current_language_code
    ).autocomplete(content_auto=question)

    # Sort data
    projects = [r for r in matches if r.model == I4pProjectTranslation]
    workgroups = [r for r in matches if r.model == WorkGroup]
    profiles = [r for r in matches if r.model == I4pProfile]
    
    project_serializer = ProjectSerializer(depth=0)
    project_data = project_serializer.serialize([r.object for r in projects[:3]], format='json')

    #workgroup_serializer = WorkGroupSerializer(depth=0)
    #workgroup_data = workgroup_serializer.serialize([r.object for r in workgroups[:3]], format='json')    

    #profile_serializer = I4pProfileSerializer(depth=0)
    #profile_data = profile_serializer.serialize([r.object for r in profiles[:3]], format='json')


    print "jdjspsjosjd"
    
    data = project_data
    
    return HttpResponse(data, content_type='application/json')


