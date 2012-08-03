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

from apps.project_sheet.models import I4pProject, I4pProjectTranslation
from apps.project_sheet.utils import get_project_translations_from_parents

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
    class Meta:
        fields = ('title', 'get_absolute_url', 'image')
    get_absolute_url = Field(source='*', convert=lambda obj: obj.get_absolute_url())
    image = Field(source='*', convert=lambda obj: obj.project.get_primary_picture().mosaic_tile.url)


def globalsearch_autocomplete(request):
    """
    Suggest results while typing in the search bar
    """
    current_language_code = translation.get_language()

    question = request.GET.get('q', '')
    
    project_translations = SearchQuerySet().models(I4pProjectTranslation).filter(language_code=current_language_code).autocomplete(content_auto=question)

        
    serializer = ProjectSerializer(depth=0, indent=4*' ')
    data = serializer.serialize([r.object for r in project_translations[:3]], format='json')

    return HttpResponse(data, content_type='application/json')


