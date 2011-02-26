import urllib

from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.utils import simplejson, translation

from dajax.core import Dajax
from dajaxice.core import dajaxice_functions

from tagging.models import Tag
from tagging.utils import get_tag_list, parse_tag_input

from .models import I4pProject, I4pProjectTranslation
from .forms import I4pProjectObjectiveForm, I4pProjectThemesForm
from .utils import get_or_create_project, get_or_create_project_translation, get_project_translation

from django.http import QueryDict, HttpResponse
from django.utils import simplejson

def project_update_related(request, language_code, related_form, project_slug):
    """
    Update themes and objective of a given project, in a given language
    """
    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation(project_translation_slug=project_slug,
                                                  language_code=language_code)

    parent_project = project_translation.project

    project_objective_form = I4pProjectObjectiveForm(related_form,
                                                     instance=parent_project)


    # Convert tags to string list, separated by comma
    if isinstance(related_form['themes'], list):
        related_form['themes'] = ", ".join(related_form['themes'])

    project_themes_form = I4pProjectThemesForm(related_form,
                                               instance=project_translation)


    if project_themes_form.is_valid() and project_objective_form.is_valid():
        # Use Tag otherwise it doesn't work because of the proxy model
        project_themes_form.save()
        #Tag.objects.update_tags(project_sheet.get_translation(), related_form['themes'])

        # Save objective
        project_objective_form.save()

    return simplejson.dumps({})


def project_sheet_edit_field(request, language_code, fieldname, value, project_slug=None):
    """
    Edit a text field
    """
    dajax = Dajax()
        
    # Activate requested language
    translation.activate(language_code)

    project_translation = get_or_create_project_translation(project_translation_slug=project_slug, 
                                                            language_code=language_code)

    FieldForm = modelform_factory(I4pProjectTranslation, fields=(fieldname,))

    form = FieldForm({fieldname: value}, instance=project_translation)
    if form.is_valid():
        form.save()
    else:
        dajax.alert("Unable to save")

    # Redirect to project sheet if it was created
    if not project_slug:
        dajax.redirect("%s#%s" % (project_translation.get_absolute_url(), fieldname))

    return dajax.json()

dajaxice_functions.register(project_sheet_edit_field)
dajaxice_functions.register(project_update_related)





