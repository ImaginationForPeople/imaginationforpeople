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
from askbot.models.user import Activity
from apps.forum.models import SpecificQuestionType, SpecificQuestion
from django.views.generic.edit import FormView
from apps.forum.forms import SpecificQuestionForm
from askbot.search.state_manager import SearchState
from askbot.views.readers import QuestionView, QuestionsView
from askbot.models.post import Post

"""
Django Views for a Project Sheet
"""
try:
    from collections import OrderedDict
except ImportError:
    # Python < 2.7 compatibility
    from ordereddict import OrderedDict

from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.utils import translation, simplejson
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.list_detail import object_list
from django.views.generic import TemplateView


from tagging.models import TaggedItem
from reversion.models import Version

from .filters import FilterSet
from .forms import I4pProjectInfoForm, I4pProjectLocationForm
from .forms import I4pProjectObjectivesForm, I4pProjectThemesForm, ProjectPictureAddForm
from .forms import ProjectReferenceFormSet, ProjectMemberAddForm, AnswerForm, ProjectVideoAddForm
from .models import Answer, I4pProjectTranslation, ProjectPicture, ProjectVideo, SiteTopic, Topic
from .models import ProjectMember, I4pProject, VERSIONNED_FIELDS, Question
from .utils import build_filters_and_context
from .utils import get_or_create_project_translation_from_parent, get_or_create_project_translation_by_slug, create_parent_project
from .utils import get_project_translation_by_slug, get_project_translation_from_parent
from .utils import get_project_project_translation_recent_changes, fields_diff
from .utils import get_project_translation_by_any_translation_slug


class CurrentProjectTranslationMixin(object):
    
    def get_project_translation(self, slug):
        language_code = translation.get_language()
        site = Site.objects.get_current()
        
        try:
            project_translation = get_project_translation_by_any_translation_slug(
                                                project_translation_slug=slug,
                                                prefered_language_code=language_code,
                                                site=site)
            
                        
        except I4pProjectTranslation.DoesNotExist:
            raise Http404
        
        return project_translation

def project_sheet_list(request):
    """
    Display a listing of all projects
    """
    language_code = translation.get_language()

    data = request.GET.copy()

    filter_forms_dict, extra_context = build_filters_and_context(data)

    ordered_project_sheets = I4pProjectTranslation.objects.none()
    filters = FilterSet(filter_forms_dict.values())

    if filters.is_valid():
        # First pass to filter project
        filtered_projects = filters.apply_to(queryset=I4pProject.on_site.all(),
                                             model_class=I4pProject)
        # Second pass to select language and site
        project_sheet_ids = []
        for project in filtered_projects:
            project_sheet = get_project_translation_from_parent(project,
                                                                language_code,
                                                                fallback_language='en',
                                                                fallback_any=True)
            project_sheet_ids.append(project_sheet.id)
        i18n_project_sheets = I4pProjectTranslation.objects.filter(id__in=project_sheet_ids)

        # Third pass to filter sheet
        filtered_project_sheets = filters.apply_to(queryset=i18n_project_sheets,
                                                   model_class=I4pProjectTranslation)

        # Fourth pass to order sheet
        if data.get("order") == "creation":
            ordered_project_sheets = filtered_project_sheets.order_by('-project__created')
            extra_context["order"] = "creation"
        elif data.get("order") == "modification":
            ordered_project_sheets = filtered_project_sheets.order_by('-modified')
            extra_context["order"] = "modification"
        else:
            # By default, display the project listing using the following order: 
            # best_of, random().
            # We need the ordering to be stable within a user session session.
            # As a hashing function, use a hopefully portable pure SQL
            # implementation (using only basic sql operators) of 
            # Knuth Variant on Division hashing algorithm: h(k) = k(k+3) mod m
            # Here the number of buckets (m) is determined by the day of the
            # year
            day_of_year = int(datetime.now().strftime('%j'))
            pseudo_random_field = "(project_id * (project_id + 3)) %% {0:d}".format(day_of_year)
            ordered_project_sheets = filtered_project_sheets.extra(select={'pseudo_random': pseudo_random_field}, order_by = ['-project__best_of','pseudo_random'])

        if data.has_key('page'):
            del data["page"]
        extra_context["getparams"] = data.urlencode()
        extra_context["orderparams"] = extra_context["getparams"]\
                                        .replace("order=creation", "")\
                                        .replace("order=modification", "")

        extra_context["selected_tags"] = [int(t.id) for t in filter_forms_dict["themes_filter"].cleaned_data["themes"]]


    extra_context.update(filter_forms_dict)
    extra_context["filters_tab_selected"] = True

    return object_list(request,
                       template_name='project_sheet/page/project_list.html',
                       queryset=ordered_project_sheets,
                       # paginate_by=12,
                       allow_empty=True,
                       template_object_name='project_translation',
                       extra_context=extra_context)

class ProjectStartView(TemplateView):
    """
    When one starts a project, after having selected a topic
    """
    template_name = 'project_sheet/page/project_sheet.html'

    def get_context_data(self, topic_slug, **kwargs):
        context = super(ProjectStartView, self).get_context_data(**kwargs)

        topic = get_object_or_404(Topic,
                                  slug=topic_slug)

        context['topic'] = topic

        return context

class ProjectTopicSelectView(TemplateView):
    """
    Before starting a project, one needs to pick a topic
    """
    template_name = 'project_sheet/obsolete/topic_select.html'

    def get(self, request, *args, **kwargs):
        site = Site.objects.get_current()
        
        self.site_topics = SiteTopic.objects.filter(site=site)

        # In case we only have one topic, don't prompt the useryep
        if len(self.site_topics) == 1:
            return redirect('project_sheet-start', self.site_topics[0].topic.slug, permanent=False)

        return super(ProjectTopicSelectView, self).get(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(ProjectTopicSelectView, self).get_context_data(**kwargs)
        context['site_topics'] = self.site_topics
        return context


class ProjectView(TemplateView):
    """
    Display a project sheet
    """
    template_name = 'project_sheet/page/project_sheet.html'

    def dispatch(self, request, *args, **kwargs):
        # Get project translation first
        language_code = translation.get_language()        
        site = Site.objects.get_current()
        slug = kwargs['slug']

        try:
            self.project_translation = get_project_translation_by_any_translation_slug(project_translation_slug=slug,
                                                                                       prefered_language_code=language_code,
                                                                                       site=site)
        except I4pProjectTranslation.DoesNotExist:
            raise Http404

        if self.project_translation.language_code != language_code:
            return redirect(self.project_translation, permanent=False)

        return super(ProjectView, self).dispatch(request, *args, **kwargs)
            
    def post(self, request, slug, *args, **kwargs):
        # Info form
        project_info_form = I4pProjectInfoForm(request.POST,
                                               instance=self.project_translation.project)
        if project_info_form.is_valid():
            project_info_form.save()
    
    def get_context_data(self, slug, *args, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
            
        # Forms
        project_member_add_form = ProjectMemberAddForm()
        # project_member_formset = ProjectMemberFormSet(queryset=project_translation.project.detailed_members.all())
        project_status_choices = OrderedDict((k, unicode(v)) 
                                             for k, v in I4pProject.STATUS_CHOICES)
        
        project = self.project_translation.project

        # Fetch questions
        topics = []
        for topic in Topic.objects.filter(site_topics=project.topics.all()):
            questions = []
            for question in topic.questions.all().order_by('weight'):
                answers = Answer.objects.filter(project=project, question=question)
                questions.append([question, answers and answers[0] or None])
            topics.append([topic, questions])
                
        project_status_choices['selected'] = self.project_translation.project.status

        # Related projects
        related_projects = TaggedItem.objects.get_related(self.project_translation,
                                                          I4pProjectTranslation.objects.exclude(project__id=project.id),
                                                          num=3)

        context.update({
            'topics': topics,
            'project': project,
            'project_translation': self.project_translation,
            'project_status_choices': simplejson.dumps(project_status_choices),
            'project_member_add_form': project_member_add_form,
            'project_tab' : True,
            'related_projects': related_projects,
        })
        

        return context

class ProjectAddMediaView(ProjectView):
    def get_context_data(self, **kwargs):
        context = super(ProjectAddMediaView, self).get_context_data(**kwargs)
        
        ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',
                                                                       'desc',
                                                                       'license',
                                                                       'author',
                                                                       'source'))
        
        ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))
        
        context.update({'picture_form' : ProjectPictureForm(),
                        'video_form' : ProjectVideoForm()})

        return context


class ProjectEditInfoView(ProjectView):
    """
    Edit Misc Info (website, ...)
    """
    def get(self, request, *args, **kwargs):
        self.project_info_form = I4pProjectInfoForm(instance=self.project_translation.project)
        self.project_location_form = I4pProjectLocationForm(instance=self.project_translation.project.location)
        return super(ProjectEditInfoView, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        # Misc info: website, ...
        self.project_info_form = I4pProjectInfoForm(request.POST,
                                                    instance=self.project_translation.project)

        self.project_location_form = I4pProjectLocationForm(request.POST,
                                                            instance=self.project_translation.project.location)

        if self.project_info_form.is_valid() and self.project_location_form.is_valid():
            self.project_info_form.save()
            location = self.project_location_form.save()
            if not self.project_translation.project.location:
                self.project_translation.project.location = location
                self.project_translation.project.save()
            
            return redirect(self.project_translation)
        else:
            return super(ProjectEditInfoView, self).get(request, *args, **kwargs)

    def get_context_data(self, slug, **kwargs):
        context = super(ProjectEditInfoView, self).get_context_data(slug, **kwargs)
        
        context['project_info_form'] = self.project_info_form
        context['project_location_form'] = self.project_location_form
        
        return context

@require_POST    
@login_required
def project_sheet_create_translation(request, project_slug):
    """
    Given a language and a slug, create a translation for a new language
    """
    current_language_code = translation.get_language()
    site = Site.objects.get_current()

    requested_language_code = request.POST.get("requested_language", None)
    if requested_language_code is None:
        return HttpResponseForbidden()

    try:
        current_project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                                      language_code=current_language_code)
    except I4pProjectTranslation.DoesNotExist:
        return Http404

    requested_project_translation = get_or_create_project_translation_from_parent(parent_project=current_project_translation.project,
                                                                                  language_code=requested_language_code,
                                                                                  default_title=current_project_translation.title)

    current_language = translation.get_language()
    translation.activate(requested_language_code)
    url = reverse('project_sheet-show', args=[requested_project_translation.slug])
    translation.activate(current_language)
    return redirect(url)


def project_sheet_edit_question(request, slug, question_id):
    """
    Edit a question for a given project sheet translation 

    FIXME: Not sure if this is secure. Question may be assigned to
    projects that doesn't link to them.
    """
    language_code = translation.get_language()

    # Get project
    try:
        project_translation = get_project_translation_by_slug(slug, language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    # Get question
    question = get_object_or_404(Question, id=question_id)

    # Lookup the answer. If does not exist, create it.
    try:
        untrans_answer = Answer.objects.untranslated().get(project=project_translation.project,
                                                           question=question)
        if not language_code in untrans_answer.get_available_languages():
            untrans_answer.translate(language_code)
            untrans_answer.save()
    except Answer.DoesNotExist:
        answer = Answer.objects.create(project=project_translation.project, question=question)

    answer = Answer.objects.get(project=project_translation.project,
                                question=question)

    answer_form = AnswerForm(request.POST or None, instance=answer)

    if request.method == 'POST':
        if answer_form.is_valid():
            answer = answer_form.save()
            return redirect(project_translation)

    context = {}
    context['answer_form'] = answer_form
    context['question_id'] = question_id
    context['project_slug'] = slug

    return render_to_response(template_name="project_sheet/page/project_sheet_edit_question.html",
                              dictionary=context,
                              context_instance=RequestContext(request))

    

def project_sheet_edit_field(request, field, slug=None, topic_slug=None):
    """
    Edit a translatable field of a project (such as baseline)

    FIXME This view is used for both project creation and
    editing. Should be splitted.
    """
    language_code = translation.get_language()

    if topic_slug:
        topic = get_object_or_404(Topic,
                                  slug=topic_slug)
    else:
        get_object_or_404(I4pProjectTranslation,
                          slug=slug,
                          language_code=language_code)

    
    FieldForm = modelform_factory(I4pProjectTranslation, fields=(field,))
    context = {}

    project_translation = None
    if request.method == 'POST':
        try:
            project_translation = get_project_translation_by_slug(slug, language_code)
        except I4pProjectTranslation.DoesNotExist:
            # Create parent project, then translation
            parent_project = create_parent_project(topic_slug)
            project_translation = get_or_create_project_translation_by_slug(slug,
                                                                            parent_project=parent_project,
                                                                            language_code=language_code)
        
        form = FieldForm(request.POST, request.FILES, instance=project_translation)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_sheet-show', args=[project_translation.slug]))
    else:
        try:
            project_translation = get_project_translation_by_slug(slug, language_code)

            form = FieldForm(instance=project_translation)
            context["project_translation"] = project_translation
        except I4pProjectTranslation.DoesNotExist:
            form = FieldForm()

    if project_translation:
        # context['project_objectives_form'] = I4pProjectObjectivesForm(instance=project_translation.project, prefix="objectives-form")
        context['project_member_form'] = ProjectMemberAddForm()
        context['answer_form'] = AnswerForm()
        context['project_tab'] = True
        context['project'] = project_translation.project
    elif topic_slug:
        context['topic'] = topic

    context["%s_form" % field] = form
    return render_to_response(template_name="project_sheet/page/project_sheet.html",
                              dictionary=context,
                              context_instance=RequestContext(request))


class ProjectEditTagsView(ProjectView):
    """
    Edit tags a given project sheet.
    Non-Ajax version.
    """
    def get_context_data(self, slug, *args, **kwargs):
        context = super(ProjectEditTagsView, self).get_context_data(slug, *args, **kwargs)

        context.update({
            'project_sheet_themes_form': self.project_sheet_themes_form,
            'project_sheet_objectives_form': self.project_sheet_objectives_form
        })
                       
        return context
    
    def get(self, request, *args, **kwargs):
        self.project_sheet_themes_form = I4pProjectThemesForm(instance=self.project_translation)

        self.project_sheet_objectives_form = I4pProjectObjectivesForm(instance=self.project_translation.project,
                                                                      prefix="objectives-form")

        return super(ProjectEditTagsView, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        self.project_sheet_themes_form = I4pProjectThemesForm(request.POST,
                                                              instance=self.project_translation)

        self.project_sheet_objectives_form = I4pProjectObjectivesForm(request.POST,
                                                                      instance=self.project_translation.project,
                                                                      prefix="objectives-form")

        if self.project_sheet_themes_form.is_valid() and self.project_sheet_objectives_form.is_valid():
            self.project_sheet_themes_form.save()
            self.project_sheet_objectives_form.save()

            return redirect(self.project_translation)
        else:
            return super(ProjectEditTagsView, self).post(request, *args, **kwargs)


class ProjectGalleryView(ProjectView):
    """
    Display a page of the gallery of the project
    """
    template_name = 'project_sheet/page/gallery.html'
    
            
def project_sheet_add_media(request):
    """
    Display a page where it is possible to submit either a video or
    picture
    Only call when the project is not yet created, else it's project_sheet_show with add_media=True
    that is called.
    """
    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',
                                                                   'desc',
                                                                   'license',
                                                                   'author',
                                                                   'source'))

    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))

    context = {'picture_form' : ProjectPictureForm(),
               'video_form' : ProjectVideoForm()}

    return render_to_response("project_sheet/project_sheet.html",
                              context,
                              context_instance=RequestContext(request))

class ProjectGalleryAddPictureView(ProjectGalleryView):
    """
    Add a picture to a project
    """
    def get(self, request, *args, **kwargs):
        self.picture_form = ProjectPictureAddForm()
        return super(ProjectGalleryAddPictureView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.picture_form = ProjectPictureAddForm(request.POST, request.FILES)
        if self.picture_form.is_valid():
            picture = self.picture_form.save(commit=False)
            picture.project = self.project_translation.project
            picture.save()

            return redirect('project_sheet-instance-gallery', self.project_translation.slug, permanent=False)
        else:
            return super(ProjectGalleryAddPictureView, self).get(request, *args, **kwargs)

    def get_context_data(self, slug, **kwargs):
        context = super(ProjectGalleryAddPictureView, self).get_context_data(slug, **kwargs)
        context['project_picture_add'] = self.picture_form
        
        return context

@login_required
def project_sheet_del_picture(request, slug, pic_id):
    """
    Delete a picture from a project sheet
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    picture = ProjectPicture.objects.filter(project=project_translation.project, id=pic_id)
    picture.delete()

    return redirect('project_sheet-instance-gallery', project_translation.slug, permanent=False)


class ProjectGalleryAddVideoView(ProjectGalleryView):
    """
    Add a video to a project
    """
    def get(self, request, *args, **kwargs):
        self.video_form = ProjectVideoAddForm()
        return super(ProjectGalleryAddVideoView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.video_form = ProjectVideoAddForm(request.POST, request.FILES)
        if self.video_form.is_valid():
            video = self.video_form.save(commit=False)
            video.project = self.project_translation.project
            video.save()

            return redirect('project_sheet-instance-gallery', self.project_translation.slug, permanent=False)
        else:
            return super(ProjectGalleryAddVideoView, self).get(request, *args, **kwargs)

    def get_context_data(self, slug, **kwargs):
        context = super(ProjectGalleryAddVideoView, self).get_context_data(slug, **kwargs)
        context['project_video_add'] = self.video_form
        
        return context

@login_required
def project_sheet_del_video(request, slug, vid_id):
    """
    Delete a video from a project sheet
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    video = ProjectVideo.objects.filter(project=project_translation.project, id=vid_id)
    video.delete()

    return redirect('project_sheet-instance-gallery', project_translation.slug, permanent=False)


class ProjectEditReferencesView(ProjectView):
    """
    Edit references of a project
    """
    def get_context_data(self, slug, *args, **kwargs):
        context = super(ProjectEditReferencesView, self).get_context_data(slug, *args, **kwargs)
        context['reference_formset'] = self.reference_formset
        return context
    
    def get(self, request, *args, **kwargs):
        self.reference_formset = ProjectReferenceFormSet(queryset=self.project_translation.project.references.all())
        return super(ProjectEditReferencesView, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        self.reference_formset = ProjectReferenceFormSet(request.POST,
                                                         queryset=self.project_translation.project.references.all())

        if self.reference_formset.is_valid():
            refs = self.reference_formset.save()
            for ref in refs:
                self.project_translation.project.references.add(ref)

        next_url = request.POST.get("next", None)
        if next_url:
            return redirect(next_url)

        return redirect(self.project_translation)


class ProjectMemberAddView(ProjectView):
    """
    When someone wants to join a project
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectMemberAddView, self).dispatch(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        self.project_member_add_form = ProjectMemberAddForm()
        return super(ProjectMemberAddView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.project_member_add_form = ProjectMemberAddForm(request.POST, request.FILES)

        # check if not yet member
        if request.user in self.project_translation.project.members.all():
            return redirect(self.project_translation)
        
        if self.project_member_add_form.is_valid():
            project_member = self.project_member_add_form.save(commit=False)
            project_member.project = self.project_translation.project
            project_member.user = request.user
            project_member.save()

            return redirect(self.project_translation)
        else:
            return super(ProjectMemberAddView, self).get(request, *args, **kwargs)
        
    def get_context_data(self, slug, *args, **kwargs):
        context = super(ProjectMemberAddView, self).get_context_data(slug, *args, **kwargs)
        context['project_member_add_form'] = self.project_member_add_form
        return context

@require_POST
@login_required
def project_sheet_member_delete(request, project_slug, username):
    """
    Delete a project member
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    parent_project = project_translation.project

    project_member = get_object_or_404(ProjectMember,
                                       user__username=username,
                                       project=parent_project)

    project_member.delete()

    return redirect(project_translation)


def project_sheet_history(request, project_slug):
    """
    Show the history of a project member
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    parent_project = project_translation.project

    #versions = Version.objects.get_for_object(project_translation).order_by('revision__date_created')

    project_translation_ct = ContentType.objects.get_for_model(project_translation)
    parent_project_ct = ContentType.objects.get_for_model(parent_project)

    versions = Version.objects.filter(Q(content_type=project_translation_ct,
                                        object_id=unicode(project_translation.id)) |
                                      Q(content_type=parent_project_ct,
                                        object_id=unicode(parent_project.id))).order_by('-revision__date_created')

    project_translation_previous_version = None
    parent_project_previous_version = None

    for version in versions:
        #Directly modify object in query set in order to keep order
        if version.content_type == project_translation_ct:
            if project_translation_previous_version:
                version.diff = fields_diff(project_translation_previous_version,
                                           version,
                                           VERSIONNED_FIELDS[project_translation_ct.model_class()])
            project_translation_previous_version = version
        else:# version.content_type == parent_project_ct:
            if parent_project_previous_version:
                version.diff = fields_diff(parent_project_previous_version,
                                           version,
                                           VERSIONNED_FIELDS[parent_project_ct.model_class()])
            parent_project_previous_version = version


    return render_to_response('project_sheet/obsolete/history.html',
                              {'project_translation' : project_translation,
                               'versions' : versions,
                               'history_tab' : True},
                              context_instance=RequestContext(request))


class ProjectRecentChangesView(TemplateView):
    template_name = 'project_sheet/obsolete/all_recent_changes.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectRecentChangesView, self).get_context_data(**kwargs)

        twenty_days_ago = datetime.now() - timedelta(days=30)

        project_translation_ct = ContentType.objects.get_for_model(I4pProjectTranslation)
        parent_project_ct = ContentType.objects.get_for_model(I4pProject)
        
        versions = Version.objects.filter(Q(content_type=project_translation_ct) | Q(content_type=parent_project_ct)).filter(revision__date_created__gt=twenty_days_ago).order_by('-revision__date_created')

        context['history'] = get_project_project_translation_recent_changes(versions)

        return context

class SpecificQuestionTypeMixin(object):
    qtypes = None
    
    def get_specific_types(self):
        assert self.qtypes != None
        query = None
        for t in self.qtypes:
            if query:
                query |= Q(key=t)
            else:
                query = Q(key=t)
                
        return SpecificQuestionType.objects.filter(query)

class SpecificQuestionListView(SpecificQuestionTypeMixin, QuestionsView):
    template_name = None
    is_specific = False
    jinja2_rendering = False
    
    def get_context_object_instance(self, **kwargs):
        raise "Must be implemented"
    
    def get_questions_url(self):
        raise "Must be implemented"
    
    def get_ask_url(self):
        raise "Must be implemented"
    
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
    template_name = None
    form_class = SpecificQuestionForm
    
    def get_success_url(self):
        raise "Must be implemented"
    
    def get_context_object_instance(self, **kwargs):
        raise "Must be implemented"
    
    def get_current_question(self, **kwargs):
        question_id = kwargs.get("question_id", None)
        if question_id:
            current_question = SpecificQuestion.objects.get(content_type=ContentType.objects.get_for_model(self.context_instance),
                                                                 object_id=self.context_instance.id,
                                                                 thread=Post.objects.get(id=question_id).thread)
        else:
            current_question = None
        return current_question
    
    def get_initial(self):
        initial = FormView.get_initial(self)
        
        initial.update({
            'content_type' : ContentType.objects.get_for_model(self.context_instance),
            'object_id' :  self.context_instance.id
        })
        
        if self.current_question:
            initial.update({
                'type' : self.current_question.type,
                'title' : self.current_question.thread.title,
                'text' : self.current_question.thread.question.text
            })
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)

        context.update({
            'search_state' : None,
        })
        
        return context
    
    def get_cleaned_tags(self, request):
        raise "Must be implemented"
    
    def form_valid(self, form):
        profile = self.request.user.get_profile()
        title = form.cleaned_data['title']
        text = form.cleaned_data['text']
        
        if self.current_question:
            profile.edit_question(
                question = self.current_question.thread.question,
                title = title,
                body_text = text,
                revision_comment = "support edition",
                tags = self.get_cleaned_tags(self.request))
            
        else :
            post = profile.post_question(
                language_code = translation.get_language(),
                site= Site.objects.get_current(),
                title = title,
                body_text = text,
                tags = self.get_cleaned_tags(self.request),
                timestamp = datetime.now()
            )
            form.instance.thread = post.thread
            form.save()
            
        return FormView.form_valid(self, form)
    
    def get(self, request, *args, **kwargs):
        self.context_instance = self.get_context_object_instance(**kwargs)
        self.current_question = self.get_current_question(**kwargs)
        return FormView.get(self, request, **kwargs)
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.context_instance = self.get_context_object_instance(**kwargs)
        self.current_question = self.get_current_question(**kwargs)
        return FormView.post(self, request)

class ProjectDiscussionListView(CurrentProjectTranslationMixin, SpecificQuestionListView): 
    template_name = "project_questions/page/global_question_list.html"
    qtypes=['pj-discuss']
    
    def get_context_object_instance(self, **kwargs):
        return self.get_project_translation(kwargs["project_slug"])
        
    def get_questions_url(self):
        return reverse('project_discussion_list', args=[self.context_object.slug])

    def get_ask_url(self):
        return reverse('project_discussion_open', args=[self.context_object.slug])

    def get_context_data(self, **kwargs):
        context = SpecificQuestionListView.get_context_data(self, **kwargs)
          
        context.update({  
            'project' : self.context_object.project,
            'project_translation' : self.context_object,
            'tab_context' : 'project_sheet',
            'tab_name' : 'discuss',
        })
    
        return context
    
class ProjectDiscussionCreateView(CurrentProjectTranslationMixin, SpecificQuestionCreateView):
    template_name = "project_questions/page/open_discussion_form.html"
    qtypes=['pj-discuss']
    
    def get_success_url(self):
        return reverse('project_discussion_list', args=[self.context_instance.slug])

    def get_context_data(self, **kwargs):
        context = SpecificQuestionCreateView.get_context_data(self, **kwargs)

        context.update({
            'project_translation' : self.context_instance,
        })
        
        return context
    
    def get_cleaned_tags(self, request):
        return "%s,%s", _("discuss"), self.context_instance.slug
    
    def get_context_object_instance(self, **kwargs):
        return self.get_project_translation(kwargs["project_slug"])
    
class ProjectDiscussionThreadView(CurrentProjectTranslationMixin, QuestionView):
    template_name = "project_questions/page/question_thread.html"
    jinja2_rendering = False
    
    def get_context_data(self, **kwargs):
        context = QuestionView.get_context_data(self, **kwargs)
        
        project_translation = self.get_project_translation(kwargs["project_slug"])
    
        search_state = SearchState.get_empty()
        search_state._questions_url = reverse('project_discussion_list', args=[project_translation.slug])
        
        context.update({
             'project' : project_translation.project,
             'project_translation' : project_translation,
             'active_tab' : 'discussion',
             'form_answer_url' : reverse('project_discussion_answer', 
                                         args=[kwargs["project_slug"], 
                                               kwargs["question_id"]]),
             'edit_question_url' : reverse('project_discussion_edit', 
                                           args=[kwargs["project_slug"], 
                                                 kwargs["question_id"]]),
             'search_state' : search_state,
             'disable_retag' : True,
        })
        
        return context