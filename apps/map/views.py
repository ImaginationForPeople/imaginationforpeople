from django.utils import translation
from django.contrib.sites.models import Site
from django.views.generic.base import View
from django.template.loader import render_to_string
from django.http import HttpResponse

from apps.project_sheet.models import I4pProject

import json

from datetime import datetime

class ProjectListJsonView(View):  

    def get(self, request, *args, **kwargs):
        
        language_code = translation.get_language()
        site = Site.objects.get_current()
        
        begin = datetime.now()                                
        projects = I4pProject.objects.language(language_code=language_code).filter(site=site, 
                                                                                   location__geom__isnull=False)
        
        step = datetime.now()
        print step - begin
        
        data = [[project.id, 
                 project.location.geom.coords[0], 
                 project.location.geom.coords[1]] 
                for project in projects]

        
        print datetime.now() - step
        return HttpResponse(json.dumps(data),
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