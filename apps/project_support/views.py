from apps.project_sheet.models import I4pProjectTranslation
from apps.project_sheet.utils import \
    get_project_translation_by_any_translation_slug
from apps.project_sheet.views import ProjectDiscussionListView, ProjectDiscussionCreateView, ProjectDiscussionThreadView,ProjectDiscussionNewAnswerView,\
    CurrentProjectTranslationMixin, SpecificQuestionTypeMixin,\
    SpecificQuestionListView
from apps.tags.models import TaggedCategory
from askbot.views.writers import edit_answer
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils import translation
from django.http import Http404
from django.utils.http import urlquote
from django.template.defaultfilters import slugify
from askbot.views.readers import QuestionsView, QuestionView
from askbot.models.question import Thread
from apps.forum.models import SpecificQuestion
from askbot.models.user import Activity
        
class ProjectSupportListView(ProjectDiscussionListView) :
    template_name = "project_support/project_support_list.html"
    qtypes=['pj-need', 'pj-help']
    
    def get_questions_url(self):
        return reverse('project_support_main', args=[self.context_object.slug])

    def get_ask_url(self):
        return reverse('project_support_propose', args=[self.context_object.slug])

    def get_context_data(self, **kwargs):
        context = ProjectDiscussionListView.get_context_data(self, **kwargs)
        
        allowed_categories = self.get_specific_types().values_list('allowed_category_tree', flat=True).distinct()
        root_category = None
        if allowed_categories.count():
            root_category = TaggedCategory.objects.get(id=allowed_categories[0])
        
        context.update({
            'tab_name' : 'support',
            'prop_count' : self.get_specific_questions().filter(type__type="pj-help").count(),
            'call_count' : self.get_specific_questions().filter(type__type="pj-need").count(),
            'need_count' : self.get_specific_questions().count(),
            'root_category' : root_category,
        })
        
        return context

class ProjectSupportListAll(SpecificQuestionListView):
    template_name = "project_support/project_support_list_all.html"
    qtypes=['pj-need', 'pj-help']

    def get_questions_url(self):
        return reverse('project_support_list_all')

    def get_ask_url(self):
        return reverse('project_support_list_all')
    
    def get_context_object_instance(self, **kwargs):
        return None
    
    def get_specific_questions(self):
        return SpecificQuestion.objects.filter(type__in=self.get_specific_types())
    
    def get_context_data(self, **kwargs):
        context = SpecificQuestionListView.get_context_data(self, **kwargs)
        
        allowed_categories = self.get_specific_types().values_list('allowed_category_tree', flat=True).distinct()
        root_category = None
        if allowed_categories.count():
            root_category = TaggedCategory.objects.get(id=allowed_categories[0])
        
        context.update({
            'tab_name' : 'support',
            'prop_count' : self.get_specific_questions().filter(type__type="pj-help").count(),
            'call_count' : self.get_specific_questions().filter(type__type="pj-need").count(),
            'need_count' : self.get_specific_questions().count(),
            'root_category' : root_category,
        })
        
        return context

class ProjectSupportCreateView(ProjectDiscussionCreateView):
    template_name = 'project_support/project_support_form.html'
    qtypes=['pj-need', 'pj-help']
    
    def get_success_url(self):
        return reverse('project_support_main', args=[self.context_instance.slug])

    def get_context_data(self, **kwargs):
        context = ProjectDiscussionCreateView.get_context_data(self, **kwargs)
        
        allowed_categories = self.get_specific_types().values_list('allowed_category_tree', flat=True).distinct()
        root_category = None
        if allowed_categories.count():
            root_category = TaggedCategory.objects.get(id=allowed_categories[0])
        
        context.update({
            'root_category' : root_category,
        })
        
        if self.current_question:
            context["current_category"] = self.current_question.thread.tags.all()[0].taggedcategory.id
        
        return context
    
    def get_cleaned_tags(self, request):
        category = TaggedCategory.objects.get(id=self.request.POST['category'])
        return category.tag.name


class ProjectSupportThreadView(ProjectDiscussionThreadView):
    qtypes=['pj-need', 'pj-help']
    
    def get_question_url(self):
        return reverse('project_support_view', args=[self.context_instance.slug,
                                                        self.current_question.thread.question.id])
    
    def get_answer_url(self):
        return reverse('project_support_answer', args=[self.context_instance.slug,
                                                        self.current_question.thread.question.id])
    
    def get_edit_url(self):
        return reverse('project_support_edit', args=[self.context_instance.slug,
                                                        self.current_question.thread.question.id])
    
    def get_context_object_instance(self, **kwargs):
        return self.get_project_translation(kwargs["project_slug"])
    
    def get_questions_url(self):
        return reverse('project_support_main', args=[self.context_instance.slug])
    
    
    def get_context_data(self, **kwargs):
        context = ProjectDiscussionThreadView.get_context_data(self, **kwargs)
        
        context.update({
             'active_tab' : 'support',
        })
        
        return context

class ProjectSupportNewAnswerView(ProjectDiscussionNewAnswerView):

    def get_success_url(self):
        return reverse('project_support_view', args=[self.context_instance.slug, 
                                                     self.current_question.id])
    
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
                       template_name="project_support/project_support_answer_edit.html",
                       extra_context=extra_context)

