from django.utils import translation
from django.contrib.sites.models import Site
from django.views.generic.base import View
from django.template.loader import render_to_string
from django.http import HttpResponse

from apps.project_sheet.models import I4pProject

class ProjectListAsGeojsonView(View):  

    def get(self, request, *args, **kwargs):
        
        language_code = translation.get_language()
        site = Site.objects.get_current()
                                              
        projects = I4pProject.objects.language(language_code=language_code).filter(site=site, location__geom__isnull=False)
        
        geojsondata = render_to_string("map/projects.geojson", 
                                       {'projects' : projects})
        return HttpResponse(geojsondata,
                            mimetype='application/json')
        
class ProjectCardAjaxView(View):  

    def get(self, request, *args, **kwargs):
        
        language_code = translation.get_language()
        site = Site.objects.get_current()
                                              
        project = I4pProject.objects.get(id=request.GET.get("project_id"),
                                         site=site)
        
        card = render_to_string("map/project_card.html", 
                                {'project' : project})
        return HttpResponse(card,
                            mimetype='application/html')