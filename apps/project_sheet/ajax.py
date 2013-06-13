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

import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.template.defaultfilters import linebreaksbr, urlize
from django.utils import simplejson, translation
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST

from honeypot.decorators import check_honeypot
from reversion import revision
from hvad.utils import get_translation_aware_manager
from apps.i4p_base.models import VersionActivity
from apps.i4p_base.utils import action_create, make_diffs_for_object

from .models import I4pProjectTranslation, I4pProject, Answer, Question
from .forms import I4pProjectObjectivesForm, I4pProjectStatusForm
from .utils import get_project_translation_by_slug

TEXTFIELD_MAPPINGS = {
    'about_section_txt': 'about_section',
    'project_partners_txt': 'partners_section',
    'project_translation_progress' : 'completion_progress',
    }

MODELFIELD_MAPPINGS = {
    'project_uniqueness_txt': 'uniqueness_section',
    'project_value_txt': 'value_section',
    'project_scalability_txt': 'scalability_section',
    'project_triggering_factor_txt': 'triggering_factor_section',
    'project_business_model_txt': 'business_model_section',
    }

_ANSWER_RE = re.compile(r'^answer-(\d+)$')


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
        id = request.GET['id']
    except KeyError:
        return HttpResponseBadRequest()

    # Check if we allow this field
    section = id
    if section in TEXTFIELD_MAPPINGS:
        return _textfield_load(language_code, project_slug, section)

    # Or check if it's an answer to a question
    question = _ANSWER_RE.search(id)
    if question:
        return _answer_load(language_code, project_slug,
                            question.groups()[0])

    return HttpResponseNotFound()


def _textfield_load(language_code, project_slug, section):
    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                          language_code=language_code)

    # Get the text
    choices = project_translation._meta.get_field(TEXTFIELD_MAPPINGS[section]).choices
    if choices:  #it's possible because choices are Charfield
        choice_dict = {}
        for key, value in choices:
            choice_dict[key] = u"%s" % value
        choice_dict["selected"] = getattr(project_translation, TEXTFIELD_MAPPINGS[section])
        resp = simplejson.dumps(choice_dict)
    else:
        resp = getattr(project_translation, TEXTFIELD_MAPPINGS[section]) or ''

    return HttpResponse(resp)


def _answer_load(language_code, project_slug, question):
    site = Site.objects.get_current()
    # Activate requested language
    translation.activate(language_code)
    project = get_object_or_404(get_translation_aware_manager(I4pProject),
                                            slug=project_slug,
                                            language_code=language_code,
                                            site=site)

    try:
        answer_content = get_translation_aware_manager(Answer).get(project__id=project.id,
                               question__id=question).content
    except Answer.DoesNotExist:
        # The answer translation may not exist yet, (new project sheet)
        # The answer may not be translated yet (new translation)
        # Both are normal, we don't create the answer yet to respect REST
        # principles
        answer_content = ''
    return HttpResponse(answer_content)


@check_honeypot(field_name='description')
@require_POST
def project_textfield_save(request, project_slug=None):
    """
    Edit a text field
    """
    try:
        language_code = request.POST['language_code']
        id = request.POST['id']
        value = request.POST['value']
    except KeyError:
        return HttpResponseBadRequest()

    # Activate requested language
    translation.activate(language_code)

    project_translation = get_project_translation_by_slug(project_slug,
                                                          language_code)

    # Check if we allow this field
    section = id
    if section in TEXTFIELD_MAPPINGS:
        return _textfield_save(request, language_code, project_slug,
                               project_translation, section, value)

    # Check if it's an answer to a question
    question = _ANSWER_RE.search(id)
    if question:
        return _answer_save(request, language_code, project_slug, project_translation,
                            question.groups()[0], value)

    return HttpResponseNotFound()

    
@revision.create_on_success
def _answer_save(request, language_code, project_slug, project_translation, question, value):
    project = project_translation.master
    question = get_object_or_404(Question, id=question)

    if value:
        #It looks like there are unforeseen consequences to a nani changeset:https://github.com/KristianOellegaard/django-hvad/commit/aba974f79bdaf9fff46c01b1d4b3e941032d02dd
        #It tries to create duplicate entries in the db
        #answer, created = Answer.objects.language(language_code).get_or_create(project=project,
        #                                                                       question=question)
        #Let's work around it:
        base_answer, created = Answer.objects.untranslated().get_or_create(project=project,
                                                                      question=question)

        if created or language_code not in base_answer.get_available_languages():
            answer = base_answer.translate(language_code)
        else:
            answer = Answer.objects.language(language_code).get(pk=base_answer.pk)
        #End workaround
        
        # Remove html tags
        value = strip_tags(value)
        answer.content = value
        answer.save()
        
        # Generate a diff
        diffs = make_diffs_for_object(answer.translations.get(language_code=language_code),
                                      'content',
                                      answer.content)

        if request.user.is_anonymous():
            revision.user = User.objects.get(id=settings.ANONYMOUS_USER_ID)
        else:
            revision.user = request.user

        # Create an action
        answer_action = action_create(actor=request.user, verb='edit_pjquestion', action_object=answer, target=project)
        revision.add_meta(VersionActivity, action=answer_action, diffs=diffs)
        
        response_dict = dict(text=linebreaksbr(urlize(value)), # Make line breaks and link urls
                             redirect=project_slug is None,
                             redirect_url=project.get_absolute_url())

        return HttpResponse(simplejson.dumps(response_dict), 'application/json')
    else:
        return HttpResponseNotFound()

@revision.create_on_success
def _textfield_save(request, language_code, project_slug, project_translation, section, value):
    # Resolve the fieldname
    fieldname = TEXTFIELD_MAPPINGS[section]
    FieldForm = modelform_factory(I4pProjectTranslation, fields=(fieldname,))

    # prevent html tags from being saved
    value = strip_tags(value)
    
    form = FieldForm({fieldname: value}, instance=project_translation)

    if form.is_valid():
        response_dict = {}
        project_translation = form.save()
        if project_translation._meta.get_field(fieldname).choices:
            text = getattr(project_translation, "get_%s_display" % fieldname)()
            if fieldname == "completion_progress":
                response_dict["completion_progress"] = getattr(project_translation,fieldname)
        else:
            # Generate line breaks and link urls if found
            text = linebreaksbr(urlize(value))

        if request.user.is_anonymous():
            revision.user = User.objects.get(id=settings.ANONYMOUS_USER_ID)
        else:
            revision.user = request.user
        project = project_translation.master
        pj_translation_action = action_create(actor=request.user, verb='edit_pjfield', action_object=project_translation, target=project)
        revision.add_meta(VersionActivity, action=pj_translation_action)
            
        response_dict.update({'text': text or '',
                              'redirect': project_slug is None,
                              'redirect_url': project_translation.master.get_absolute_url()})

        return HttpResponse(simplejson.dumps(response_dict), 'application/json')
    else:
        return HttpResponseNotFound()


@login_required
def project_sheet_edit_status(request, slug):
    """
    Change the status (concept, work in progress, etc.) of a project.
    """
    language_code = translation.get_language()

    # get the project translation and its base
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug=slug,
                                                              language_code=language_code)
    except I4pProjectTranslation.DoesNotExist:
        raise Http404

    # Status
    project_status_form = I4pProjectStatusForm(request.POST,
                                               instance=project_translation.master)

    if request.method == 'POST' and project_status_form.is_valid():
        project_status_form.save()
        # Reload project_translation
        project_translation = get_project_translation_by_slug(project_translation_slug=slug,
                                                              language_code=language_code)
        return render_to_response(template_name='project_sheet/project_status.html',
                dictionary={'project_translation': project_translation},
                context_instance=RequestContext(request))
    else:
        return HttpResponseBadRequest()

@require_POST
def project_update_related(request, project_slug):
    """
    Update themes and objectives of a given project, in a given language
    """
    language_code = request.POST['language_code']

    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                          language_code=language_code)

    parent_project = project_translation.master

    themes = ", ".join(request.POST.getlist('themes'))
    project_translation.themes = themes
    project_translation.save()

    project_objectives_form = I4pProjectObjectivesForm(request.POST,
                                                       instance=parent_project,
                                                       prefix="objectives-form")
    if  project_objectives_form.is_valid():
        project_objectives_form.save()

    return redirect(reverse('project_sheet-show',
                            kwargs={'slug': project_slug}))


