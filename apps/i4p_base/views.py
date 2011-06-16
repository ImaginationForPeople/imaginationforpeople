# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.utils import translation

from apps.project_sheet.models import I4pProject
from apps.project_sheet.utils import get_project_translations_from_parents, build_filters_and_context

def homepage(request):
    """
    I4P Homepage
    """
    project_sheets = I4pProject.objects.filter(best_of=True).order_by('?')[:14]
    project_translations = get_project_translations_from_parents(project_sheets,
                                                                 language_code=translation.get_language()
                                                                 )

    context = {'project_sheets': project_sheets,
               'project_translations': project_translations,
               'about_tab_selected' : True}

    filter_forms, extra_context = build_filters_and_context(request.GET)
    context.update(filter_forms)
    context.update(extra_context)


    return render_to_response(template_name='homepage.html',
                              dictionary=context,
                              context_instance=RequestContext(request)
                              )







