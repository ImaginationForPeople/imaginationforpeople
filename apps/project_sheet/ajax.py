import urllib

from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from dajax.core import Dajax
from dajaxice.core import dajaxice_functions

from tagging.utils import get_tag_list, parse_tag_input

from .models import I4pProject
from .forms import I4pProjectRelatedForm
from .views import get_or_create_project

def urldecode(query):
    d = {}
    a = query.split('&')
    for s in a:
        if s.find('='):
            k,v = map(urllib.unquote, s.split('='))
            try:
                d[k].append(v)
            except KeyError:
                d[k] = [v]
                
    return d


def project_update_related(request, related_form, project_slug):
    """
    Update theme of a given project
    """
    dajax = Dajax()

    # hack to get the theme tags in the good format
    # "ex, am, ple"
    data = urldecode(related_form)

    print "xxx",  data['objective'][0]

    themes = ""
    for theme in data['themes']:
        themes += theme + ", "
    data['themes'] = themes
    data['objective'] = data['objective'][0]

    # get the project or create it
    project_sheet = get_or_create_project(request, project_slug)

    project_themes_form = I4pProjectRelatedForm(data,
                                                instance=project_sheet)

    if project_themes_form.is_valid():
        project_themes_form.save()
    else:
        dajax.alert("Unable to save")

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
    else:
        dajax.alert("Unable to save")

    # Redirect to project sheet if it was created
    if not project_slug:
        dajax.redirect("%s#%s" % (project.get_absolute_url(), fieldname))

    return dajax.json()

dajaxice_functions.register(project_sheet_edit_field)
dajaxice_functions.register(project_update_related)





