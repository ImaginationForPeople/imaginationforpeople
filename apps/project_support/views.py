import datetime

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.utils import translation
from django.views.generic.base import TemplateView

from askbot.models import Thread

from apps.project_sheet.models import I4pProjectTranslation
from apps.project_sheet.utils import get_project_translation_by_any_translation_slug
from apps.project_support.forms import ProjectSupportProposalForm

from apps.project_support.models import ProjectSupport

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
        
        thread_ids = project_translation.projectsupport_set.values_list('thread', flat=True)
        threads = Thread.objects.filter(id__in=thread_ids)
        
        prop_count = project_translation.projectsupport_set.filter(type="PROP").count()
        call_count = project_translation.projectsupport_set.filter(type="CALL").count()
        
        extra_context = {
             'project' : project,
             'project_translation' : project_translation,
             'active_tab' : 'support',
             'threads' : threads,
             'prop_count' : prop_count,
             'call_count' : call_count
         }
        
        context.update(extra_context)

        return context
    
def propose_project_support(request, project_slug):

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
        
        
        if request.method == "POST":
            form = ProjectSupportProposalForm(request.POST,
                                              initial={'project_translation': project_translation})
            if form.is_valid():
                timestamp = datetime.datetime.now()
                support_type = form.cleaned_data['type']
                title = form.cleaned_data['title']
                category = form.cleaned_data['category']
                text = form.cleaned_data['text']

                if request.user.is_authenticated():
                
                    profile = request.user.get_profile()
            
                    question = profile.post_question(
                        language_code = language_code,
                        site= site,
                        title = title,
                        body_text = text,
                        tags = category.tag.name,
                        timestamp = timestamp
                    )
                    
                    if support_type == "PROP":
                        support = ProjectSupport.objects.create(project_translation=project_translation,
                                                                        type=support_type,
                                                                        category=category,
                                                                        thread=question.thread)
                    else:
                        raise "Not Yep Implemented"
                    
                    
                    return HttpResponseRedirect(reverse('project_support_main', args=[project_slug]))
        else:
            form = ProjectSupportProposalForm(initial={'project_translation': project_translation})

        context = {
            'project_translation' : project_translation,
            'form' : form,
        }
        
        return render_to_response("project_support/project_support_form.html",
                                  dictionary=context,
                                  context_instance=RequestContext(request))
