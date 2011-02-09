# -*- coding: utf-8 -*-

from .forms import I4pProjectTitleFieldForm,\
    I4pProjectBaselineFieldForm, I4pProjectAboutFieldForm,\
    I4pProjectUniquenessFieldForm, I4pProjectValueFieldForm,\
    I4pProjectScalabilityFieldForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _

def edit_project_sheet(request):
    title_form = I4pProjectTitleFieldForm(initial={'title' : _("my project title")})
    baseline_form = I4pProjectBaselineFieldForm(initial={'baseline' : _("my project\'s baseline")})
    about_form = I4pProjectAboutFieldForm()
    uniqueness_form = I4pProjectUniquenessFieldForm()
    value_form = I4pProjectValueFieldForm()
    scalability_form = I4pProjectScalabilityFieldForm()
                                     
    return render_to_response("project_sheet.html",
                              {'title_form' : title_form,
                               'baseline_form' : baseline_form,
                               'about_form' : about_form,
                               'uniqueness_form' : uniqueness_form,
                               'value_form' : value_form,
                               'scalability_form' : scalability_form},
                              context_instance = RequestContext(request))