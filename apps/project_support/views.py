import datetime

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.utils import translation

from askbot.models import Thread, Activity, Post
from askbot.views.readers import question, QuestionsView
from askbot.views.writers import answer, edit_answer

from apps.project_sheet.models import I4pProjectTranslation
from apps.project_sheet.utils import get_project_translation_by_any_translation_slug
from apps.project_support.forms import ProjectSupportProposalForm

from apps.project_support.models import ProjectSupport
from apps.tags.models import TaggedCategory
from askbot.search.state_manager import SearchState
from apps.project_sheet.views import CurrentProjectTranslationMixin
    
class ProjectSupportListView(CurrentProjectTranslationMixin, QuestionsView) :
    template_name = "project_support/project_support_list.html"
    is_specific = True
    jinja2_rendering = False
    
    def get_context_data(self, **kwargs):
        project_translation = self.get_project_translation(kwargs["project_slug"])
        
        self.questions_url = reverse('project_support_main', args=[project_translation.slug])
        self.ask_url = reverse('project_support_propose', args=[project_translation.slug])
        
        self.thread_ids = project_translation.projectsupport_set.values_list('thread', flat=True)
        
        context = QuestionsView.get_context_data(self, **kwargs)
        
        threads = Thread.objects.filter(id__in=self.thread_ids)
        
        prop_count = project_translation.projectsupport_set.filter(type="PROP").count()
        call_count = project_translation.projectsupport_set.filter(type="CALL").count()
        
        activity_ids = []
        for thread in threads:
            for post in thread.posts.all():
                activity_ids.extend(list(post.activity_set.values_list('id', flat=True)))
        activities = Activity.objects.filter(id__in=set(activity_ids)).order_by('active_at')[:5]
        
        context.update({
             'project' : project_translation.project,
             'project_translation' : project_translation,
             'active_tab' : 'support',
             'prop_count' : prop_count,
             'call_count' : call_count,
             'activities' : activities,
             'root_category' : TaggedCategory.objects.get_or_create(name='support')[0],
             'feed_url': reverse('project_support_main', args=[project_translation.slug])+"#TODO_RSS",
        })
        return context
    
def propose_project_support(request, project_slug, question_id=None):

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
        
        question = None
        initial = {}
        
        if question_id:
            question = Post.objects.get(id=question_id)
            support = ProjectSupport.objects.get(project_translation=project_translation,
                                                 thread=question.thread)
            initial = {'title': support.thread.title,
                       'text' : support.thread.question.text}
        else :
            support = ProjectSupport(project_translation=project_translation)
        
        if request.method == "POST":
            form = ProjectSupportProposalForm(request.POST,
                                              instance=support,
                                              initial=initial)
            if form.is_valid():
                title = form.cleaned_data['title']
                category = form.cleaned_data['category']
                text = form.cleaned_data['text']

                if request.user.is_authenticated():
                
                    profile = request.user.get_profile()
                    
                    if question:
                        profile.edit_question(
                            question = question,
                            title = title,
                            body_text = text,
                            revision_comment = "support edition",
                            tags = category.tag.name)
                    else:
                        question = profile.post_question(
                            language_code = language_code,
                            site= site,
                            title = title,
                            body_text = text,
                            tags = category.tag.name,
                            timestamp = datetime.datetime.now()
                        )
                    
                    form.instance.thread = question.thread
                    form.save()
                    
                    
                    return HttpResponseRedirect(reverse('project_support_main', args=[project_slug]))
        else:
            form = ProjectSupportProposalForm(instance=support,
                                              initial=initial)

        context = {
            'project_translation' : project_translation,
            'form' : form,
            'root_category' : TaggedCategory.objects.get_or_create(name='support')[0],
            'search_state' : None,
        }
        
        return render_to_response("project_support/project_support_form.html",
                                  dictionary=context,
                                  context_instance=RequestContext(request))

def view_project_support(request, project_slug, question_id):
    
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
    
    search_state = SearchState.get_empty()
    search_state._questions_url = reverse('project_support_main', args=[project_translation.slug])
    
    extra_context = {
             'project' : project,
             'project_translation' : project_translation,
             'active_tab' : 'support',
             'form_answer_url' : reverse('project_support_answer', args=[project_slug, question_id]),
             'edit_question_url' : reverse('project_support_edit', args=[project_slug, question_id]),
             'search_state' : search_state,
             'disable_retag' : True,
         }
    
    return question(request, 
                    question_id, 
                    template_name="project_support/project_support_thread.html",
                    jinja2_rendering=False,
                    extra_context=extra_context)

def answer_project_support(request, project_slug, question_id):
    return answer(request, 
                  question_id, 
                  redirect_to=reverse('project_support_view', args=[project_slug, question_id]))
    
def edit_support_answer(request, project_slug, answer_id):
    language_code = translation.get_language()
    site = Site.objects.get_current()
        
    try:
        project_translation = get_project_translation_by_any_translation_slug(project_translation_slug=project_slug,
                                            prefered_language_code=language_code,
                                            site=site)
        
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    extra_context = {
         'project_translation' : project_translation,
         'active_tab' : 'support',
    }
    
    return edit_answer(request, 
                       answer_id,
                       jinja2_rendering=False,
                       template_name="project_support/block/answer_edit.html",
                       extra_context=extra_context)

