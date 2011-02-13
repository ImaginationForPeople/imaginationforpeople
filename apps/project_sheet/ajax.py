from django.shortcuts import get_object_or_404
from dajax.core import Dajax
from dajaxice.core import dajaxice_functions

from .models import I4pProject
from .forms import I4pProjectThemesForm



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

dajaxice_functions.register(project_update_themes)





