#-- encoding: utf-8 --
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#
from askbot.models.question import Thread
from askbot.models.user import Activity
from askbot.views.readers import QuestionsView, QuestionView

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils import translation
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic import View

from guardian.decorators import permission_required_or_403
from guardian.shortcuts import assign
from wiki.core.plugins import registry as plugin_registry        
from wiki.models.article import Article, ArticleForObject, ArticleRevision
from wiki.views.article import Edit as WikiEdit

from apps.project_sheet.utils import get_project_translations_from_parents,\
    get_project_translation_by_any_translation_slug

from .models import WorkGroup
from .forms import GroupCreateForm, GroupEditForm
from .utils import get_ml_members
from apps.project_sheet.views import SpecificQuestionListView,\
    SpecificQuestionCreateView, SpecificQuestionNewAnswerView,\
    SpecificQuestionThreadView
from apps.forum.models import SpecificQuestion
from django.contrib.contenttypes.models import ContentType
from askbot.models.post import Post
from askbot.search.state_manager import SearchState
from django.utils.http import urlquote
from django.template.defaultfilters import slugify
from apps.workgroup.forms import WorkgroupDiscussionForm
from django.contrib.sites.models import Site
from django.http import Http404
from askbot.views.writers import EditAnswerView

class GroupListView(ListView):
    template_name = 'workgroup/workgroup_list.html'
    context_object_name = 'workgroup_list'
    queryset = WorkGroup.objects.all()

class GroupCreateView(CreateView):
    """
    When one wants to create a new group
    """
    form_class = GroupCreateForm
    template_name = 'workgroup/page/group_create.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GroupCreateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        res = super(GroupCreateView, self).post(request, *args, **kwargs)
        assign('change_workgroup', request.user, self.object)
        self.object.subscribers.add(request.user)
        return res

class GroupEditView(UpdateView):
    """
    When one wants to edit a group
    """
    form_class = GroupEditForm
    slug_field = 'slug'
    model = WorkGroup
    template_name = 'workgroup/page/group_edit.html'

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('change_workgroup', (WorkGroup, 'slug', 'slug')))
    def dispatch(self, request, *args, **kwargs):
        return super(GroupEditView, self).dispatch(request, *args, **kwargs)
        

class GroupDetailView(DetailView):
    template_name = 'workgroup/page/workgroup_detail.html'
    context_object_name = 'workgroup'
    model = WorkGroup

    def get_context_data(self, **kwargs):
        """
        Adds the member of the associated ML if there's one
        """
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        
        workgroup = context['workgroup']

        # Look up mailing list members
        if workgroup.mailing_list:
            context['ml_member_list'] = [] # Both on I4P & the ML
            context['ml_nonmember_list'] = [] # Only subscribed to the ML
            members = get_ml_members(workgroup)
            
            for member in members:
                try:
                    found_member = User.objects.get(email=member[0])
                    context['ml_member_list'].append(found_member)
                    
                    # Subscribe the user to the workgroup if not yet
                    if found_member not in workgroup.subscribers.all():
                        workgroup.subscribers.add(found_member)
                except User.DoesNotExist:
                    context['ml_nonmember_list'].append(User(email=member[0]))

        # Wiki
        try:
            article = Article.get_for_object(workgroup)
        except ArticleForObject.DoesNotExist:
            article = Article.objects.create()
            article.add_object_relation(workgroup)
            revision = ArticleRevision(title=workgroup.name, content='')
            article.add_revision(revision)

        context['wiki_article'] = article
        
        language_code = translation.get_language()
        project_translations = get_project_translations_from_parents(parents_qs=workgroup.projects.all(),
                                                                     language_code=language_code,
                                                                     fallback_language='en',
                                                                     fallback_any=True)
        
        context['group_projects'] = project_translations
            
        return context

class GroupDescriptionDetailView(GroupDetailView):
    """
    View to display the group description article which is a sub-article of the home article
    of the group (which is either fetched or created in GroupDetailView)
    """
    template_name = 'workgroup/page/workgroup_description.html'
    
    def get_context_data(self, **kwargs):
        context = super(GroupDescriptionDetailView, self).get_context_data(**kwargs)
        workgroup = context['workgroup']
        
        # First be sure that the home Wiki article already exists
        try:
            home_article = Article.get_for_object(workgroup)            
        except ArticleForObject.DoesNotExist:
            return redirect('workgroup-detail', slug=workgroup.slug)
        
        # now check that the description article exists
        try:
            desc_article = Article.get_for_object(home_article) 
        except ArticleForObject.DoesNotExist:    
            desc_article = Article.objects.create()
            desc_article.add_object_relation(home_article)
            revision = ArticleRevision(title="description of %s" %workgroup.name, content='')
            desc_article.add_revision(revision)

        context.update({
             'wiki_article' : desc_article,                        
        })
        
        return context

class GroupMembersView(GroupDetailView):
    """
    List all members of the given group
    """
    template_name = 'workgroup/page/workgroup_members.html'
        
class GroupWikiEdit(WikiEdit):
    template_name = "workgroup/page/wiki_edit.html"
    
    def dispatch(self, request, workgroup_slug, *args, **kwargs):
        self.workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)
        article = Article.get_for_object(self.workgroup)
        
        self.sidebar_plugins = plugin_registry.get_sidebar()
        self.sidebar = []
        
        return super(WikiEdit, self).dispatch(request, article, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(GroupWikiEdit, self).get_context_data(*args, **kwargs)
        context['workgroup'] = self.workgroup
        return context

    def get_success_url(self):
        return redirect(self.workgroup)
        
class GroupDescriptionWikiEdit(GroupWikiEdit):
    """
    View to edit the description article
    """
    template_name = "workgroup/page/workgroup_description_edit.html"
    
    def dispatch(self, request, workgroup_slug, *args, **kwargs):   
        self.workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)         
        article = Article.get_for_object(Article.get_for_object(self.workgroup)) 
        
        self.sidebar_plugins = plugin_registry.get_sidebar()
        self.sidebar = []
  
        return super(WikiEdit, self).dispatch(request, article, *args, **kwargs)
    
    def get_success_url(self):
        return redirect('workgroup-description', slug=self.workgroup.slug)
    

class SubscribeView(View):
    """
    Subscribe a user to the workgroup
    """
    @method_decorator(login_required)
    def get(self, request, workgroup_slug):
        workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)
        user = request.user

        # Subscibre the user to the workgroup
        workgroup.subscribers.add(user)
        
        # Force cache regeneration
        cache_key = '%s-ml-members' % workgroup.slug
        cache.delete(cache_key)

        # Subscribe the user to the mailing list        
        if workgroup.mailing_list:
            ml = workgroup.mailing_list
            try:
                ml.subscribe(user.email,
                             user.first_name,
                             user.last_name,
                             send_welcome_msg=True)

                messages.success(request, _(u"You have been successfully subscribed to the"
                                            u"%(workgroup_name)s mailing list"
                                            u" (%(user_email)s)" % {'workgroup_name': workgroup.name,
                                                                    'user_email': user.email}
                                            )
                                 )
            except Exception, e:
                messages.error(request, _(u"You couldn't be subscribed to this group:%s" % unicode(e.message, encoding=ml.encoding)))

        next_url = request.GET.get('next_url', None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect(workgroup)


class UnsubscribeView(View):
    """
    Unsubscribe a user to the group
    """
    @method_decorator(login_required)
    def get(self, request, workgroup_slug):
        workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)
        user = request.user

        # Removing user from workgroup
        workgroup.subscribers.remove(user)
        
        # Force cache regeneration
        cache_key = '%s-ml-members' % workgroup.slug
        cache.delete(cache_key)

        # removing user from mailing list
        if workgroup.mailing_list:
            ml = workgroup.mailing_list
            try:
                ml.unsubscribe(user.email)

                messages.success(request, _(u"You have been successfully unsubscribed from the"
                                            u"%(workgroup_name)s mailing list"
                                            u" (%(user_email)s)" % {'workgroup_name': workgroup.name,
                                                                    'user_email': user.email}
                                            )
                                 )
            except Exception, e:
                messages.error(request, _(u"You couldn't be unsubscribed from this group:%s" % e.message))

        next_url = request.GET.get('next_url', None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect(workgroup)


class GroupDiscussionListView(SpecificQuestionListView):
    """
    View to list the discussions (forum threads) linked to the current group
    """
    template_name = "workgroup/page/workgroup_discuss_list.html"
    qtypes = ["wg-discuss"]
    
    def get_context_object_instance(self, **kwargs):
        return get_object_or_404(WorkGroup, slug=kwargs["workgroup_slug"])  
    
    def get_questions_url(self):
        return reverse('workgroup-discussion', args=[self.context_object.slug])
    
    def get_ask_url(self):
        return reverse('workgroup-discussion-open', args=[self.context_object.slug])
    
    def get_context_data(self, **kwargs):
        context = SpecificQuestionListView.get_context_data(self, **kwargs)
        
        context.update({
             'active_tab' : 'discuss',
             'workgroup' : self.context_object,             
        })
    
        return context
    
class GroupDiscussionCreateView(SpecificQuestionCreateView):
    template_name = "workgroup/page/group_discuss_form.html"
    form_class = WorkgroupDiscussionForm
    qtypes = ["wg-discuss"]
    
    def get_success_url(self):
        return reverse('workgroup-discussion', args=[self.context_instance.slug])

    def get_context_data(self, **kwargs):
        context = SpecificQuestionCreateView.get_context_data(self, **kwargs)

        context.update({
            'workgroup' : self.context_instance,
        })
        
        return context
    
    def get_cleaned_tags(self, request):
        return "%s %s" % ("workgroup", self.context_instance.slug)
    
    def get_context_object_instance(self, **kwargs):
        return get_object_or_404(WorkGroup, slug=kwargs["workgroup_slug"])  
    
class GroupDiscussionThreadView(SpecificQuestionThreadView):
    template_name = "workgroup/page/group_discuss_thread.html"
    answer_controls_template_name = "workgroup/block/answer_controls.html"
    qtypes = ["wg-discuss"]
    
    def get_question_url(self):
        return reverse('workgroup-discussion-view', args=[self.context_instance.slug,
                                                        self.current_question.thread.question.id])
    
    def get_answer_url(self):
        #FIXME : set up the right URL
        return reverse('workgroup-discussion-answer', args=[self.context_instance.slug,
                                                        self.current_question.thread.question.id])
    
    def get_edit_url(self):
        #FIXME : set up the right URL
        return reverse('workgroup-discussion-edit', args=[self.context_instance.slug,
                                                        self.current_question.thread.question.id])
    
    def get_context_object_instance(self, **kwargs):
        return get_object_or_404(WorkGroup, slug=kwargs["workgroup_slug"]) 
    
    def get_questions_url(self):
        return reverse('workgroup-discussion', args=[self.context_instance.slug])
    
    
    def get_context_data(self, **kwargs):
        context = SpecificQuestionThreadView.get_context_data(self, **kwargs)
        
        context.update({
             'workgroup' : self.context_instance,
             'active_tab' : 'discussion',
        })
        
        return context

class GroupDiscussionNewAnswerView(SpecificQuestionNewAnswerView):
    def get_success_url(self):
        return reverse('workgroup-discussion-view', args=[self.context_instance.slug, 
                                                     self.current_question.id])

    def get_context_object_instance(self, **kwargs):
        return get_object_or_404(WorkGroup, slug=kwargs["workgroup_slug"]) 


class GroupDiscussionEditAnswerView(EditAnswerView):
    template_name="workgroup/page/group_discuss_answer_edit.html"
    
    def dispatch(self, request, *args, **kwargs):
        self.workgroup = get_object_or_404(WorkGroup, slug=kwargs["workgroup_slug"])
        return EditAnswerView.dispatch(self, request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('workgroup-discussion-view', args=[self.workgroup.slug, 
                                                     self.current_question.id])
        
    def get_context_data(self, answer_id, **kwargs):
        context = EditAnswerView.get_context_data(self, answer_id, **kwargs)
        
        context.update({
            'workgroup' : self.workgroup,
            'active_tab' : 'workgroup',
         })

        return context
