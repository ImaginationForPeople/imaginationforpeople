
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound, QueryDict, Http404
from django.utils import translation
from django.views.decorators.http import require_POST
from django.views.generic.list_detail import object_list
from django.db.models import Q

from localeurl.templatetags.localeurl_tags import chlocale
from reversion.models import Version

from .forms import I4pProjectThemesForm, I4pProjectObjectiveForm, I4pProjectInfoForm, ProjectReferenceFormSet, I4pProjectLocationForm, ProjectMemberForm, ProjectMemberFormSet
from .models import ProjectPicture, ProjectVideo, I4pProjectTranslation, ProjectMember, I4pProject, VERSIONNED_FIELDS
from .utils import get_or_create_project_translation_from_parent, get_or_create_project_translation_by_slug, get_project_translation_by_slug, get_project_translation_from_parent
from .filters import FilterSet
from apps.project_sheet.utils import build_filters_and_context
from django.contrib.auth.decorators import login_required

def project_sheet_list(request):
    """
    Display a listing of all projects
    """
    language_code = translation.get_language()

    data = request.GET

    filter_forms, extra_context = build_filters_and_context(data)

    ordered_project_sheets = None
    filters = FilterSet(filter_forms)

    if filters.is_valid():
        #First pass to filter project
        filtered_projects = filters.apply_to(queryset=I4pProject.objects.all(),
                                             model_class=I4pProject)
        #Second pass to select language
        project_sheet_ids = []
        for project in filtered_projects:
            project_sheet = get_project_translation_from_parent(project,
                                                                language_code,
                                                                fallback_language='en',
                                                                fallback_any=True)
            project_sheet_ids.append(project_sheet.id)
        i18n_project_sheets = I4pProjectTranslation.objects.filter(id__in=project_sheet_ids)

        #Third pass to filter sheet
        filtered_project_sheets = filters.apply_to(queryset=i18n_project_sheets,
                                                   model_class=I4pProjectTranslation)

        #Fourth pass to order sheet
        if data.get("order") == "creation":
            ordered_project_sheets = filtered_project_sheets.order_by('-project__created')
            extra_context["order"] = "creation"
        elif data.get("order") == "modification":
            ordered_project_sheets = filtered_project_sheets.order_by('-modified')
            extra_context["order"] = "modification"
        else:
            ordered_project_sheets = filtered_project_sheets.order_by('-project__best_of', 'slug')

        extra_context["getparams"] = data.urlencode()
        extra_context["orderparams"] = extra_context["getparams"]\
                                        .replace("order=creation", "")\
                                        .replace("order=modification", "")

        extra_context["selected_tags"] = [int(t.id) for t in filter_forms["themes_filter"].get_tags()]

    else:
        pass

    extra_context.update(filter_forms)
    extra_context["filters_tab_selected"] = True

    return object_list(request,
                       template_name='project_sheet/project_list.html',
                       queryset=ordered_project_sheets,
                       paginate_by=12,
                       allow_empty=True,
                       template_object_name='project_translation',
                       extra_context=extra_context)

def project_sheet_show(request, slug):
    """
    Display a project sheet
    """
    language_code = translation.get_language()

    project_translation = get_object_or_404(I4pProjectTranslation,
                                            slug=slug,
                                            language_code=language_code)

    project_themes_form = I4pProjectThemesForm(instance=project_translation)
    project_objective_form = I4pProjectObjectiveForm(instance=project_translation.project)

    # Member
    project_member_form = ProjectMemberForm(request.POST or None)
    if request.method == 'POST' and project_member_form.is_valid():
        project_member = project_member_form.save(commit=False)
        project_member.project = project_translation.project
        project_member.save()

    project_member_formset = ProjectMemberFormSet(queryset=project_translation.project.detailed_members.all())

    # Info
    project_info_form = I4pProjectInfoForm(request.POST or None,
                                           instance=project_translation.project)
    if request.method == 'POST' and project_info_form.is_valid():
        project_info_form.save()

    # Location
    project_location_form = I4pProjectLocationForm(request.POST or None,
                                                   instance=project_translation.project.location)
    if request.method == 'POST' and project_location_form.is_valid():
        location = project_location_form.save()
        if not project_translation.project.location:
            project_translation.project.location = location
            project_translation.project.save()

    reference_formset = ProjectReferenceFormSet(queryset=project_translation.project.references.all())

    return render_to_response(template_name='project_sheet/project_sheet.html',
                              dictionary={'project': project_translation.project,
                                          'project_translation': project_translation,
                                          'project_themes_form': project_themes_form,
                                          'project_objective_form': project_objective_form,
#                                          'reference_form' : reference_form,
                                          'reference_formset' : reference_formset,
                                          'project_info_form': project_info_form,
                                          'project_location_form': project_location_form,
                                          'project_member_form': project_member_form,
                                          'project_member_formset': project_member_formset,
                                          'project_tab' : True},
                              context_instance=RequestContext(request)
                              )

@login_required
def project_sheet_create_translation(request, project_slug, requested_language_code):
    """
    Given a language and a slug, create a translation for a new language
    """
    current_language_code = translation.get_language()

    try:
        current_project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                                      language_code=current_language_code)
    except I4pProjectTranslation.DoesNotExist:
        return HttpResponseNotFound()

    requested_project_translation = get_or_create_project_translation_from_parent(parent_project=current_project_translation.project,
                                                                                  language_code=requested_language_code,
                                                                                  default_title=current_project_translation.title)

    url = reverse('project_sheet-show', args=[requested_project_translation.slug])
    return redirect(chlocale(url, requested_language_code))


def project_sheet_edit_field(request, field, slug=None):
    """
    Edit a translatable field of a project (such as baseline)
    """
    language_code = translation.get_language()

    FieldForm = modelform_factory(I4pProjectTranslation, fields=(field,))
    context = {}

    if request.method == 'POST':
        project_translation = get_or_create_project_translation_by_slug(slug, language_code)
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

    context["%s_form" % field] = form
    return render_to_response(template_name="project_sheet/project_sheet.html",
                              dictionary=context,
                              context_instance=RequestContext(request))


def project_sheet_edit_related(request, project_slug):
    """
    Edit themes (using tags) of a given project sheet.
    Non-Ajax version.
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    parent_project = project_translation.project

    project_sheet_themes_form = I4pProjectThemesForm(request.POST or None,
                                                     instance=project_translation)

    project_sheet_objective_form = I4pProjectObjectiveForm(request.POST or None,
                                                           instance=parent_project)

    if request.method == 'POST':
        if project_sheet_themes_form.is_valid() and project_sheet_objective_form.is_valid():
            project_sheet_themes_form.save()
            project_sheet_objective_form.save()

            return redirect(project_translation)

    dictionary = {'project_translation': project_translation,
                  'project_sheet_themes_form': project_sheet_themes_form,
                  'project_sheet_objective_form': project_sheet_objective_form}

    return render_to_response(template_name="project_sheet/project_edit_themes.html",
                              dictionary=dictionary,
                              context_instance=RequestContext(request)
                              )


def project_sheet_add_media(request, slug=None):
    """
    Display a page where it is possible to submit either a video or
    picture
    """
    language_code = translation.get_language()

    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',
                                                                   'desc',
                                                                   'license',
                                                                   'author',
                                                                   'source'))

    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))

    context = {'picture_form' : ProjectPictureForm(),
               'video_form' : ProjectVideoForm()}

    try :
        context["project_translation"] = get_project_translation_by_slug(project_translation_slug=slug,
                                                                         language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
            pass

    return render_to_response("project_sheet/project_sheet.html",
                              context,
                              context_instance=RequestContext(request))

def project_sheet_add_picture(request, slug=None):
    """
    Add a picture to a project
    """
    language_code = translation.get_language()

    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',
                                                                   'desc',
                                                                   'license',
                                                                   'author',
                                                                   'source'))

    project_translation = get_or_create_project_translation_by_slug(project_translation_slug=slug,
                                                                    language_code=language_code)

    if request.method == 'POST':
        picture_form = ProjectPictureForm(request.POST, request.FILES)
        if picture_form.is_valid():
            picture = picture_form.save(commit=False)
            picture.project = project_translation.project
            picture.save()

    return redirect(project_translation)

def project_sheet_del_picture(request, slug, pic_id):

    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    picture = ProjectPicture.objects.filter(project=project_translation.project, id=pic_id)
    picture.delete()

    return redirect(project_translation)

def project_sheet_add_video(request, slug=None):
    """
    Embed a video to a project
    """
    language_code = translation.get_language()

    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))

    project_translation = get_or_create_project_translation_by_slug(project_translation_slug=slug,
                                                                    language_code=language_code)

    if request.method == 'POST':
        video_form = ProjectVideoForm(request.POST)
        if video_form.is_valid():
            video = video_form.save(commit=False)
            video.project = project_translation.project
            video.save()

    return redirect(project_translation)

def project_sheet_del_video(request, slug, vid_id):

    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    video = ProjectVideo.objects.filter(project=project_translation.project, id=vid_id)
    video.delete()

    return redirect(project_translation)


@require_POST
def project_sheet_edit_references(request, project_slug):
    """
    Edit references of a project
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    parent_project = project_translation.project

    reference_formset = ProjectReferenceFormSet(request.POST, queryset=parent_project.references.all())

    if reference_formset.is_valid():
        refs = reference_formset.save()
        for ref in refs:
            parent_project.references.add(ref)

    next = request.POST.get("next", None)
    if next:
        return HttpResponseRedirect(next)

    return redirect(project_translation)


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
                                        object_id=unicode(parent_project.id))).order_by('revision__date_created')

    version_field_diff = {}
    project_translation_previous_version = None
    parent_project_previous_version = None

    def fields_diff(previous_version, current_version, versionned_fields):
        fields = []
        previous_field_dict = previous_version.get_field_dict()
        current_field_dict = current_version.get_field_dict()
        for field, value in current_field_dict.iteritems():
            if field in versionned_fields and field in previous_field_dict and previous_field_dict[field] != value:
                fields.append(version.content_type.model_class()._meta.get_field(field).verbose_name + '')
        return fields

    for version in versions:
        if version.content_type == project_translation_ct:
            if project_translation_previous_version:
                version_field_diff[version] = fields_diff(project_translation_previous_version,
                                                          version,
                                                          VERSIONNED_FIELDS[project_translation_ct.model_class()])
            project_translation_previous_version = version
        elif version.content_type == parent_project_ct:
            if parent_project_previous_version:
                version_field_diff[version] = fields_diff(parent_project_previous_version,
                                                          version,
                                                          VERSIONNED_FIELDS[parent_project_ct.model_class()])
            parent_project_previous_version = version

    return render_to_response('project_sheet/history.html',
                              {'project_translation' : project_translation,
                               'versions' : version_field_diff,
                               'history_tab' : True},
                              context_instance=RequestContext(request))

