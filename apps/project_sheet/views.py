# -*- coding: utf-8 -*-

from django.conf import settings 
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.utils import translation
from django.views.decorators.http import require_POST

from localeurl.templatetags.localeurl_tags import chlocale

from .forms import I4pProjectThemesForm, I4pProjectObjectiveForm
from .models import I4pProject, ProjectPicture, ProjectVideo, I4pProjectTranslation
from .utils import get_or_create_project_translation, get_project_translation

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

    return render_to_response(template_name='project_sheet.html', 
                              dictionary={'project_translation': project_translation,
                                          'project_themes_form': project_themes_form,
                                          'project_objective_form': project_objective_form},
                              context_instance = RequestContext(request))


@require_POST
def project_sheet_create_translation(request, project_slug):
    """
    Given a language and a slug, create a translation for a new language
    """
    requested_language_code = request.POST['language_code']
    current_language_code = translation.get_language()
    
    try:
        current_project_translation = get_project_translation(project_translation_slug=project_slug,
                                                              language_code=current_language_code)
    except I4pProjectTranslation.DoesNotExist:
        return HttpResponseNotFound()

    requested_project_translation = get_or_create_project_translation(project_translation_slug=project_slug,
                                                                      language_code=requested_language_code,
                                                                      parent_project=current_project_translation.project,
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
        project_translation = get_or_create_project_translation(slug, language_code)
        form = FieldForm(request.POST, request.FILES, instance=project_translation)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_sheet-show', args=[project_translation.slug]))
    else:
        try:
            project_translation = get_project_translation(slug, language_code)

            form = FieldForm(instance=project_translation)
            context["project_translation"] = project_translation
        except I4pProjectTranslation.DoesNotExist:
            form = FieldForm()

    context["%s_form" % field] =  form
    return render_to_response(template_name="project_sheet.html",
                              dictionary=context,
                              context_instance=RequestContext(request))


def project_sheet_edit_related(request, project_slug):
    """
    Edit themes (using tags) of a given project sheet.
    Non-Ajax version.
    """
    language_code = translation.get_language()

    # get the project translation and its base
    project_translation = get_project_translation(project_translation_slug=project_slug,
                                                  language_code=language_code)

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

    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',))
    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))
    
    context = {'picture_form' : ProjectPictureForm(),
               'video_form' : ProjectVideoForm()}
    
    try :
        context["project_translation"] = get_project_translation(project_translation_slug=slug,
                                                                 language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
            pass

    return render_to_response("project_sheet.html",
                              context, 
                              context_instance = RequestContext(request))

def project_sheet_add_picture(request, slug=None):
    """
    Add a picture to a project
    """
    language_code = translation.get_language()

    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',))
    
    project_translation = get_or_create_project_translation(project_translation_slug=slug,
                                                            language_code=language_code)
    
    if request.method == 'POST':
        picture_form = ProjectPictureForm(request.POST, request.FILES)
        if picture_form.is_valid():
            picture = picture_form.save(commit=False)
            picture.project = project_translation.project
            picture.save()

    return redirect(project_translation)

def project_sheet_add_video(request, slug=None):
    """
    Embed a video to a project
    """
    language_code = translation.get_language()

    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))
    
    project_translation = get_or_create_project_translation(project_translation_slug=slug,
                                                            language_code=language_code)
    
    if request.method == 'POST':
        video_form = ProjectVideoForm(request.POST)
        if video_form.is_valid():
            video = video_form.save(commit=False)
            video.project = project_translation.project
            video.save()

    return redirect(project_translation)
