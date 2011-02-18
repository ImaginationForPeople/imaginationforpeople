# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect

from .forms import I4pProjectRelatedForm
from .models import I4pProject, I4pProfile, ProjectPicture, ProjectVideo

def get_or_create_project(request, slug):
    try:
        project =  I4pProject.objects.get(slug=slug)
    except I4pProject.DoesNotExist:
        profile = None
        if request.user.is_authenticated():
            try:
                profile = I4pProfile.objects.get(user=request.user)
            except I4pProfile.DoesNotExist:
                pass
        ip_addr = request.META["REMOTE_ADDR"]
        project = I4pProject.objects.create(author=profile,
                                            ip_addr=ip_addr)
    
    return project

def project_sheet_show(request, slug):
    """
    Display a project sheet
    """
    project_related_form = I4pProjectRelatedForm()

    project = get_object_or_404(I4pProject, slug=slug)

    return render_to_response(template_name='project_sheet.html', 
                              dictionary={'project_instance': project,
                                          'project_related_form': project_related_form},
                              context_instance = RequestContext(request))

   
def project_sheet_edit_field(request, field, slug=None, model_class=I4pProject):
    FieldForm = modelform_factory(model_class, fields=(field,))
    context = {}
    if request.method == 'POST':
        project = get_or_create_project(request, slug)
        form = FieldForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_sheet-show', args=[project.slug]))
    else:
        try:
            project =  I4pProject.objects.get(slug=slug)
            form = FieldForm(instance=project)
            context["project_instance"] = project
        except I4pProject.DoesNotExist:
            form = FieldForm()

    context["%s_form" % field] =  form
    return render_to_response("project_sheet.html",
                              context,
                              context_instance = RequestContext(request))

def project_sheet_edit_related(request, project_slug):
    """
    Edit themes (using tags) of a given project sheet.
    Non-Ajax version.
    """
    project_sheet = get_object_or_404(I4pProject, slug=project_slug)

    project_sheet_related_form = I4pProjectRelatedForm(request.POST or None, 
                                                      instance=project_sheet)

    if request.method == 'POST':
        if project_sheet_related_form.is_valid():
            project_sheet_related_form.save()
            return redirect(project_sheet)

    dictionary = {'project_sheet': project_sheet,
                  'project_sheet_related_form': project_sheet_related_form}

    return render_to_response(template_name="project_sheet/project_edit_themes.html",
                              dictionary=dictionary,
                              context_instance=RequestContext(request)
                              )


def project_sheet_add_media(request, slug=None):
    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',))
    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))
    
    context = {'picture_form' : ProjectPictureForm(),
               'video_form' : ProjectVideoForm()}
    
    try :
        context["project_instance"] = I4pProject.objects.get(slug=slug)
    except I4pProject.DoesNotExist:
            pass

    return render_to_response("project_sheet.html",
                              context, 
                              context_instance = RequestContext(request))

def project_sheet_add_picture(request, slug=None):
    ProjectPictureForm = modelform_factory(ProjectPicture, fields=('original_image',))
    
    project = get_or_create_project(request, slug)
    
    if request.method == 'POST':
        picture_form = ProjectPictureForm(request.POST, request.FILES)
        if picture_form.is_valid():
            picture = picture_form.save(commit=False)
            picture.project = project
            picture.save()
        else :
            print picture_form.errors

    return redirect(project)

def project_sheet_add_video(request, slug=None):
    ProjectVideoForm = modelform_factory(ProjectVideo, fields=('video_url',))
    
    project = get_or_create_project(request, slug)
    
    if request.method == 'POST':
        video_form = ProjectVideoForm(request.POST, request.FILES)
        if video_form.is_valid():
            video = video_form.save(commit=False)
            video.project = project
            video.save()
        else :
            print video_form.errors

    return redirect(project)
