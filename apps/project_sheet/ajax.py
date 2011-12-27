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
"""
Ajax views for handling project sheet creation and edition.
"""
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.template.defaultfilters import linebreaksbr
from django.utils import simplejson, translation
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from dajaxice.core import dajaxice_functions

from honeypot.decorators import check_honeypot

from .models import I4pProjectTranslation
from .forms import I4pProjectObjectivesForm, I4pProjectThemesForm
from .utils import get_or_create_project_translation_by_slug, get_project_translation_by_slug

TEXTFIELD_MAPPINGS = {
    'about_section_txt': 'about_section',
    'project_uniqueness_txt': 'uniqueness_section',
    'project_value_txt': 'value_section',
    'project_scalability_txt': 'scalability_section',
    'project_triggering_factor_txt': 'triggering_factor_section',
    'project_partners_txt': 'partners_section',
    'project_business_model_txt': 'business_model_section',
    'project_translation_progress' : 'completion_progress',
    }

def project_textfield_load(request, project_slug=None):
    """
    Load the source of a text field (project description, ...),
    without the markup rendered (useful for JS editing, to prevent
    html tags from being edited without interpretation).
    """
    if not project_slug:
        return HttpResponse('')

    try:
        language_code = request.GET['language_code']
        section = request.GET['id']
    except KeyError:
        return HttpResponseBadRequest()

    # Check if we allow this field
    if not section in TEXTFIELD_MAPPINGS:
        return HttpResponseNotFound()

    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                          language_code=language_code)

    # Get the text
    choices = project_translation._meta.get_field(TEXTFIELD_MAPPINGS[section]).choices
    if choices : # it's possible because choices are Charfield
        choice_dict = {}
        for key, value in choices:
            choice_dict[key] = u"%s" % value
        choice_dict["selected"] = getattr(project_translation, TEXTFIELD_MAPPINGS[section])
        resp = simplejson.dumps(choice_dict)
    else:
        resp = getattr(project_translation, TEXTFIELD_MAPPINGS[section]) or ''

    return HttpResponse(resp)

@check_honeypot(field_name='description')
@require_POST
@csrf_exempt
def project_textfield_save(request, project_slug=None):
    """
    Edit a text field
    """
    language_code = request.POST['language_code']
    section = request.POST['id']
    value = request.POST['value']

    # Activate requested language
    translation.activate(language_code)

    project_translation = get_or_create_project_translation_by_slug(project_translation_slug=project_slug, 
                                                                    language_code=language_code)
    
    # Check if we allow this field
    if not section in TEXTFIELD_MAPPINGS:
        return HttpResponseNotFound()

    # Resolve the fieldname
    fieldname = TEXTFIELD_MAPPINGS[section]
    print fieldname
    FieldForm = modelform_factory(I4pProjectTranslation, fields=(fieldname,))

    form = FieldForm({fieldname: value}, instance=project_translation)

    if form.is_valid():
        response_dict = {}
        form.save()
        if project_translation._meta.get_field(fieldname).choices:
            text = getattr(project_translation, "get_%s_display" % fieldname)()
            if fieldname == "completion_progress" :
                response_dict["completion_progress"] = getattr(project_translation,fieldname)
        else:
            text = linebreaksbr(value)
        
        response_dict.update({'text': text or '',
                              'redirect': project_slug is None,
                              'redirect_url': project_translation.get_absolute_url()})
        
        return HttpResponse(simplejson.dumps(response_dict), 'application/json')
    else:
        return HttpResponseNotFound()


def project_update_related(request, language_code, related_form, project_slug):
    """
    Update themes and objectives of a given project, in a given language
    """
    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                          language_code=language_code)

    parent_project = project_translation.project


    # Convert tags to string list, separated by comma
    if not related_form.has_key('themes'):
        related_form['themes'] = ""
        
    if isinstance(related_form['themes'], list):
        related_form['themes'] = ", ".join(related_form['themes'])
            
    project_themes_form = I4pProjectThemesForm(related_form,
                                               instance=project_translation)
            
    if project_themes_form.is_valid():
        project_themes_form.save()


    # Convert objectives to list if string or empty
    if not related_form.has_key('objectives-form-objectives'):
        related_form['objectives-form-objectives'] = []
        
    if not isinstance(related_form['objectives-form-objectives'], list):
        related_form['objectives-form-objectives'] = related_form['objectives-form-objectives'].split(',')

    project_objectives_form = I4pProjectObjectivesForm(related_form,
                                                       instance=parent_project,
                                                       prefix="objectives-form")

    if  project_objectives_form.is_valid():
        project_objectives_form.save()


        
    return simplejson.dumps({})


# Dajax Registration
dajaxice_functions.register(project_update_related)





