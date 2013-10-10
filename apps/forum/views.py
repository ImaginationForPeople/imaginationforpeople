from datetime import datetime

from django.db.models import Q
from django.views.generic.edit import FormView
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils import translation
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import urlquote
from django.template.defaultfilters import slugify
from django.http import Http404

from askbot.models.user import Activity
from askbot.search.state_manager import SearchState
from askbot.views.readers import QuestionView, QuestionsView
from askbot.models.post import Post
from askbot.views.writers import PostNewAnswerView
from askbot.utils import decorators

from .models import SpecificQuestionType, SpecificQuestion, QUESTION_TYPE_CHOICES
from .forms import SpecificQuestionForm



class SpecificQuestionTypeMixin(object):
    """
    Provide method to deal with specific question type
    """
    qtypes = None
    
    def get_specific_types(self):
        if self.qtypes == None:
            raise AttributeError("qtypes must be initialized")
        
        for t in self.qtypes:
            assert t in [k for (k,v) in QUESTION_TYPE_CHOICES]
        
        if len(self.qtypes) == 1:
            qs = SpecificQuestionType.objects.filter(type=self.qtypes[0])
        else:
            query = None
            for t in self.qtypes:
                if query:
                    query |= Q(type=t)
                else:
                    query = Q(type=t)
            qs = SpecificQuestionType.objects.filter(query)
        return qs

class SpecificQuestionListView(SpecificQuestionTypeMixin, QuestionsView):
    """
    Abstract CBV to list specific questions according their type
    """
    template_name = None
    is_specific = False
    jinja2_rendering = False
    
    def get_context_object_instance(self, **kwargs):
        raise NotImplementedError
    
    def get_questions_url(self):
        raise NotImplementedError
    
    def get_ask_url(self):
        raise NotImplementedError
    
    def get_specific_questions(self):
        return SpecificQuestion.objects.filter(type__in=self.get_specific_types(),
                                               content_type=ContentType.objects.get_for_model(self.context_object),
                                               object_id=self.context_object.id)
    
    def get_context_data(self, **kwargs):

        self.context_object = self.get_context_object_instance(**kwargs)
        self.thread_ids = self.get_specific_questions().values_list('thread', flat=True)

        context = QuestionsView.get_context_data(self, **kwargs)
    
        activity_ids = []
        specific_questions = []
        
        for thread in context["threads"].object_list:
            specific_questions.append(self.get_specific_questions().get(thread__id=thread.id))
            for post in thread.posts.all():
                activity_ids.extend(list(post.activity_set.values_list('id', flat=True)))
        activities = Activity.objects.filter(id__in=set(activity_ids)).order_by('active_at')[:5]
        
        context.update({
            'specific_questions' : specific_questions,
            'activities' : activities,            
        })
        
        return context
    
    
class SpecificQuestionCreateView(SpecificQuestionTypeMixin, FormView):
    """
    Abstract CBV to create a specific question according its type
    """
    template_name = None
    form_class = SpecificQuestionForm
    is_specific = False
    
    def get_success_url(self):
        raise NotImplementedError
    
    def get_context_object_instance(self, **kwargs):
        raise NotImplementedError
    
    def get_current_question(self, **kwargs):
        question_id = kwargs.get("question_id", None)
        if question_id:
            current_question = SpecificQuestion.objects.get(type__in=self.get_specific_types(),
                                                            content_type=ContentType.objects.get_for_model(self.context_instance),
                                                            object_id=self.context_instance.id,
                                                            thread=Post.objects.get(id=question_id).thread)
        else:
            current_question = None
        return current_question
    
    
    def get_initial(self):
        initial = FormView.get_initial(self)
        
        initial.update({
            'content_type': ContentType.objects.get_for_model(self.context_instance),
            'object_id': self.context_instance.id
        })
        
        if self.current_question:
            initial.update({
                'type': self.current_question.type,
                'title': self.current_question.thread.title,
                'text': self.current_question.thread.question.text
            })
        
        return initial
    
    
    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)

        context.update({
            'search_state': None,
        })
        
        return context
    
    def get_cleaned_tags(self, request):
        raise NotImplementedError
    
    def form_valid(self, form):
        profile = self.request.user.get_profile()
        title = form.cleaned_data['title']
        text = form.cleaned_data['text']
        
        if self.current_question:
            profile.edit_question(
                question=self.current_question.thread.question,
                title=title,
                body_text=text,
                revision_comment="support edition",
                tags=self.get_cleaned_tags(self.request)
            )
            
        else :
            post = profile.post_question(
                language_code=translation.get_language(),
                site=Site.objects.get_current(),
                title=title,
                body_text=text,
                tags=self.get_cleaned_tags(self.request),
                timestamp=datetime.now()
            )
            form.instance.thread = post.thread
            form.save()
            post.thread.is_specific = self.is_specific
            post.thread.save()
            
        return FormView.form_valid(self, form)
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.context_instance = self.get_context_object_instance(**kwargs)
        self.current_question = self.get_current_question(**kwargs)
        return FormView.get(self, request, **kwargs)
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.context_instance = self.get_context_object_instance(**kwargs)
        self.current_question = self.get_current_question(**kwargs)
        return FormView.post(self, request)

class SpecificQuestionThreadView(SpecificQuestionTypeMixin, QuestionView):
    """
    Abstract CBV to visualise a specific question according its type
    """
    template_name = "project_questions/page/question_thread.html"
    jinja2_rendering = False
    
    def get_question_url(self):
        raise NotImplementedError
    
    def get_answer_url(self):
        raise NotImplementedError
    
    def get_edit_url(self):
        raise NotImplementedError
    
    def get_context_object_instance(self, **kwargs):
        raise NotImplementedError
    
    def get_questions_url(self):
        raise NotImplementedError
    
    def get_context_data(self, **kwargs):
        context = QuestionView.get_context_data(self, **kwargs)
        
        self.context_instance = self.get_context_object_instance(**kwargs)
        
        try:
            self.current_question = SpecificQuestion.objects.get(type__in=self.get_specific_types(),
                                                             content_type=ContentType.objects.get_for_model(self.context_instance),
                                                             object_id=self.context_instance.id,
                                                             thread=Post.objects.get(id=kwargs["question_id"]).thread)
        except SpecificQuestion.DoesNotExist: 
            raise Http404
        
        search_state = SearchState.get_empty()
        search_state._questions_url = self.get_questions_url()
        
        context.update({
            'current_question': self.current_question,
            'current_question_url': self.get_question_url(),
            'form_answer_url': self.get_answer_url(),
            'edit_question_url': self.get_edit_url(),
            'search_state': search_state,
            'disable_retag': True,
        })
        
        return context

class SpecificQuestionNewAnswerView(PostNewAnswerView):
    """
    Abstract CBV to answer to a specific question
    """
    def get_success_url(self):
        raise NotImplementedError
    
    def get_answer_url(self, answer):
        url = u'%(base)s%(slug)s/?answer=%(id)d#post-id-%(id)d' % {
                'base': self.get_success_url(),
                'slug': urlquote(slugify(answer.thread.title)),
                'id': answer.id
            }
        return url
    
    def get_context_object_instance(self, **kwargs):
        raise NotImplementedError
        
    def post(self, request, **kwargs):
        self.context_instance = self.get_context_object_instance(**kwargs)
        return PostNewAnswerView.post(self, request, **kwargs)
