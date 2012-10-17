from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.utils import translation
from django.contrib.sites.models import Site
from apps.project_sheet.utils import get_project_translation_by_any_translation_slug
from apps.project_sheet.models import I4pProjectTranslation
from django.http import Http404

class ProjectSupportView(TemplateView):
    template_name = 'project_support/project_support.html'

    def get_context_data(self, project_slug, **kwargs):
        context = super(ProjectSupportView, self).get_context_data(**kwargs)

        language_code = translation.get_language()

        site = Site.objects.get_current()
            
        try:
            project_translation = get_project_translation_by_any_translation_slug(project_translation_slug=project_slug,
                                                prefered_language_code=language_code,
                                                site=site)
            
        except I4pProjectTranslation.DoesNotExist:
            raise Http404
    
        if project_translation.language_code != language_code:
            return redirect(project_translation, permanent=False)

        project = project_translation.project
        
        context ['project'] = project,
        context ['project_translation']  = project_translation
        context ['active_tab'] = 'support'

        return context