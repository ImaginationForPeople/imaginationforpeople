from django.utils import translation
from django.contrib.sites.models import Site
from django.views.generic.base import View

from django.template.loader import render_to_string
from django.http import HttpResponse

from apps.i4p_base.models import Location
from apps.project_sheet.models import I4pProject

import json

from datetime import datetime

class ProjectListJsonView(View):  

    def get(self, request, *args, **kwargs):
        
        language_code = translation.get_language()
        site = Site.objects.get_current()
        
        begin = datetime.now()                                
        #projects = I4pProject.objects.language(language_code=language_code).filter(site=site, locations__geom__isnull=False)
        locations = Location.objects.filter(geom__isnull=False,
                                            i4pproject__site=site,
                                            i4pproject__id__isnull=False
                                            ).prefetch_related('i4pproject_set')
        
        
        step = datetime.now()
        print step - begin
        
        data = [[location.i4pproject_set.all()[0].id,
                 location.id,
                 location.geom.coords[0], 
                 location.geom.coords[1],
                 ] 
                for location in locations]

        
        print datetime.now() - step
        return HttpResponse(json.dumps(data),
                            mimetype='application/json')

class ProjectCardAjaxView(View):  

    def get(self, request, *args, **kwargs):
        
        language_code = translation.get_language()
        site = Site.objects.get_current()
                                              
        project = I4pProject.objects.get(id=request.GET.get("project_id"),
                                         site=site)
        location = Location.objects.get(id=request.GET.get("location_id"))
                
        card = render_to_string(kwargs['template_name'], 
                                {'project' : project,
                                 'location' : location})
        return HttpResponse(card,
                            mimetype='application/html')