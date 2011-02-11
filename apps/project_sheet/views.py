# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from .models import I4pProject, I4pProfile
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory

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
    project = get_object_or_404(I4pProject, slug=slug)
    return render_to_response('project_sheet.html', 
                              {'project_instance': project},
                              context_instance = RequestContext(request))

   
def project_sheet_edit_field(request, field, slug=None):
    FieldForm = modelform_factory(I4pProject, fields=(field,))
    context = {}
    if request.method == 'POST':
        project = get_or_create_project(request, slug)
        form = FieldForm(request.POST, instance=project)
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
