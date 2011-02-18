from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from dajax.core import Dajax
from dajaxice.core import dajaxice_functions

from .models import I4pProject
from .forms import I4pProjectThemesForm
from .views import get_or_create_project

def project_update_themes(request, themes_form, project_slug):
    """
    Update theme of a given project
    """
    dajax = Dajax()

    try:
        project_sheet = I4pProject.objects.get(slug=project_slug)
    except I4pProject.DoesNotExist, e:
        raise e

    project_themes_form = I4pProjectThemesForm(themes_form,
                                               instance=project_sheet)

    if project_themes_form.is_valid():
        project_themes_form.save()
    else:
        raise "Invalid form"

    return dajax.json()


def project_sheet_edit_field(request, fieldname, value, project_slug=None):
    """
    Edit a text field
    """
    dajax = Dajax()

    FieldForm = modelform_factory(I4pProject, fields=(fieldname,))

    project = get_or_create_project(request, project_slug)

    form = FieldForm({fieldname: value}, instance=project)
    if form.is_valid():
        form.save()

    # Redirect to project sheet if it was created
    if not project_slug:
        dajax.redirect("%s#%s" % (project.get_absolute_url(), fieldname))

    return dajax.json()

dajaxice_functions.register(project_sheet_edit_field)
dajaxice_functions.register(project_update_themes)





