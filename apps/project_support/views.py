from django.core.urlresolvers import reverse

from apps.forum.models import SpecificQuestion
from apps.forum.views import SpecificQuestionListView
from apps.project_sheet.views import ProjectDiscussionListView, \
    ProjectDiscussionCreateView, ProjectDiscussionThreadView, \
    ProjectDiscussionNewAnswerView, \
    ProjectDiscussionEditAnswerView
from apps.tags.models import TaggedCategory
from .forms import ProjectSheetNeedForm

 
class ProjectSupportListView(ProjectDiscussionListView) :
    """
    List all supports related to a project sheet translation
    """
    template_name = "project_support/project_support_list.html"
    qtypes = ['pj-need', 'pj-help']
    is_specific = True
    
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
            'prop_count' : len([q for q in context["specific_questions"] if q.type.type == "pj-help"]),
            'call_count' : len([q for q in context["specific_questions"] if q.type.type == "pj-need"]),
            'need_count' : len(context["specific_questions"]),
            'root_category' : root_category,
        })
        
        return context

class ProjectSupportListAll(SpecificQuestionListView):
    """
    List all supports for all project sheets
    """
    template_name = "project_support/project_support_list_all.html"
    qtypes = ['pj-need', 'pj-help']

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
    """
    Create a support for a given project sheet translation
    """
    template_name = 'project_support/project_support_form.html'
    qtypes = ['pj-need', 'pj-help']
    form_class = ProjectSheetNeedForm
    is_specific = True
    
#     http_method_names = ['post']
    
    def get_success_url(self):
        return reverse('project_support_main', args=[self.context_instance.slug])

    def get_context_data(self, **kwargs):
        context = ProjectDiscussionCreateView.get_context_data(self, **kwargs)
        
        allowed_categories = self.get_specific_types().values_list('allowed_category_tree', flat=True).distinct()
        root_category = None
        if allowed_categories.count():
            root_category = TaggedCategory.objects.get(id=allowed_categories[0])
        
        context.update({
            'root_category': root_category,
        })
        
        if self.current_question:
            context["current_category"] = self.current_question.thread.tags.all()[0].taggedcategory.id
        
        return context
    
    def get_cleaned_tags(self, request):
        category = TaggedCategory.objects.get(id=request.POST['category'])
        return category.tag.name

class ProjectSupportThreadView(ProjectDiscussionThreadView):
    """
    Display a support thread for a given project sheet translation
    """
    qtypes = ['pj-need', 'pj-help']
    template_name = "project_support/project_support_question_thread.html"
    
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
             'active_tab': 'support',
        })
        
        return context

class ProjectSupportNewAnswerView(ProjectDiscussionNewAnswerView):
    """
    Answer to a given project sheet support question
    """
    def get_success_url(self):
        return reverse('project_support_view', args=[self.context_instance.slug,
                                                     self.current_question.id])
    
class ProjectSupportEditAnswerView(ProjectDiscussionEditAnswerView):
    """
    Edit a given project sheet support answer
    """
    def get_success_url(self):
        return reverse('project_support_view', args=[self.project_translation.slug,
                                                     self.current_question.id])
    
