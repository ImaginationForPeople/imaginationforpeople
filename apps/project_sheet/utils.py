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
Toolkit for a project sheet management
"""
from reversion.models import Version

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import DatabaseError
from django.contrib.sites.models import Site

from tagging.models import Tag

from .models import I4pProject, I4pProjectTranslation, SiteTopic, VERSIONNED_FIELDS
from .filters import BestOfFilterForm, NameBaselineFilterForm, TopicFilterForm
from .filters import ProjectStatusFilterForm, ProjectProgressFilterForm, ProjectLocationFilterForm
from .filters import ThemesFilterForm, WithMembersFilterForm, ProjectObjectiveFilterForm

def create_parent_project(topic_slug):
    """
    Create a parent project
    """
    project = I4pProject.objects.create()

    site = Site.objects.get_current().id
    project.site.add(site)

    topic = SiteTopic.objects.get(topic__slug=topic_slug, site=site)
    project.topics.add(topic)

    return project 

def get_project_translation_by_slug(project_translation_slug, language_code):
    """
    Get a translation of a given project
    """
    return I4pProjectTranslation.objects.get(language_code=language_code,
                                             slug=project_translation_slug)

def get_project_translation_by_any_translation_slug(project_translation_slug, prefered_language_code, site):
    """
    Get a translation of a given project, looking at slugs in any language
    """
    try:
        project_translation = I4pProjectTranslation.objects.get(slug=project_translation_slug,
                                            language_code=prefered_language_code,
                                            project__site=site)
        return project_translation
    except I4pProjectTranslation.DoesNotExist:
        for lang_code, lang_name in settings.LANGUAGES:
             if lang_code != prefered_language_code:
                 try:
                     project_translation = I4pProjectTranslation.objects.get(slug=project_translation_slug,
                                                language_code=lang_code,
                                                project__site=site)
                     project_best_translation = get_project_translation_from_parent(project_translation.project, prefered_language_code, fallback_language=settings.LANGUAGE_CODE, fallback_any=True)
                     return project_best_translation
                 except I4pProjectTranslation.DoesNotExist:
                     pass
    raise I4pProjectTranslation.DoesNotExist


def get_project_translation_from_parent(parent, language_code, fallback_language=None, fallback_any=False):
    """
    Get a translation of a given project.
    If we have a fallback language, try to use it.
    If we also have fallback_any, then pick the first translation.
    Otherwise, raise a DoesNotExist exception
    """
    try:
        project_translation = parent.translations.get(language_code=language_code)
    except I4pProjectTranslation.DoesNotExist, e:
        if fallback_language:
            try:
                project_translation = parent.translations.get(language_code=fallback_language)
            except I4pProjectTranslation.DoesNotExist, e:
                if fallback_any:
                    project_translation = parent.translations.all()[0]
                else:
                    raise e
        else:
            raise e
    except AttributeError:
        raise I4pProject.DoesNotExist

    return project_translation


def get_project_translations_from_parents(parents_qs, language_code, fallback_language='en', fallback_any=True):
    """
    Same as above, but given a queryset of parents
    """
    return [get_project_translation_from_parent(project,
                                                language_code=language_code,
                                                fallback_language=fallback_language,
                                                fallback_any=fallback_any
                                                )
            for project
            in parents_qs
            ]


def create_project_translation(language_code, parent_project, default_title=None):
    """
    Create a translation of a project.
    """
    try:
        I4pProjectTranslation.objects.get(project=parent_project,
                                          language_code=language_code)
        raise DatabaseError('This translation already exist')
    except I4pProjectTranslation.DoesNotExist:
        pass

    if default_title:
        project_translation = I4pProjectTranslation.objects.create(project=parent_project,
                                                                   language_code=language_code,
                                                                   title=default_title)            
    else:
        project_translation = I4pProjectTranslation.objects.create(project=parent_project,
                                                                   language_code=language_code)

    return project_translation


def get_or_create_project_translation_by_slug(project_translation_slug, language_code, parent_project, default_title=None):
    """
    Create a project translation for the given language_code with the
    given slug.

    This version does not need a parent. Beware: using it twice for
    the same language with a different slug can lead to duplicate
    projects.
    When possible, use the "_from_parent" version instead.
    """
    try:
        project_translation = get_project_translation_by_slug(project_translation_slug, language_code)
    except I4pProjectTranslation.DoesNotExist:
        project_translation = create_project_translation(language_code=language_code,
                                                         parent_project=parent_project,
                                                         default_title=default_title)

    return project_translation


def get_or_create_project_translation_from_parent(parent_project, language_code, default_title=None):
    """
    Create a project translation for the given language_code, related to a parent project (language agnostic)
    """
    try:
        project_translation = get_project_translation_from_parent(parent_project, language_code)
    except I4pProjectTranslation.DoesNotExist:
        project_translation = create_project_translation(language_code=language_code,
                                                         parent_project=parent_project,
                                                         default_title=default_title)

    return project_translation



def build_filters_and_context(request_data):
    """
    Build the set of filter in order to include them in homepage and project list page
    
    request : the GET variables passes to the view (i.e i4pbase.views.homepage or project_sheet.views.project_sheet_list)
    
    Return :
    - the set of filters form
    - an extra context
    """

    filter_forms = {
        'topic_filter' : TopicFilterForm(request_data),
        'themes_filter' : ThemesFilterForm(request_data),
        'location_filter' : ProjectLocationFilterForm(request_data),
        'best_of_filter' : BestOfFilterForm(request_data),
        'status_filter' : ProjectStatusFilterForm(request_data),
        'members_filter' : WithMembersFilterForm(request_data),
        'progress_filter' : ProjectProgressFilterForm(request_data),
        'project_sheet_search_form' : NameBaselineFilterForm(request_data),
        'objective_filter' : ProjectObjectiveFilterForm(request_data)
    }

    project_sheet_tags = Tag.objects.usage_for_model(I4pProjectTranslation, counts=True)
    project_sheet_tags.sort(key=lambda tag:-tag.count)

    extra_context = {
         "project_sheet_tags" : project_sheet_tags
    }

    return (filter_forms, extra_context)

#-- Reversion utils --#
def fields_diff(previous_version, current_version, versionned_fields):
    """
    Diff between two model fields
    """
    fields = []
    previous_field_dict = previous_version.field_dict
    current_field_dict = current_version.field_dict
    for field, value in current_field_dict.iteritems():
        if field in versionned_fields:
            if field in previous_field_dict:
                if previous_field_dict[field] != value:
                    fields.append(current_version.content_type.model_class()._meta.get_field(field).verbose_name + '')
    return fields


def get_project_project_translation_recent_changes(queryset):
    """
    Return the diff as a dict of the given version queryset
    """
    project_translation_ct = ContentType.objects.get_for_model(I4pProjectTranslation)
    parent_project_ct = ContentType.objects.get_for_model(I4pProject)

    project_translation_previous_version = None
    parent_project_previous_version = None
    
    history = []
    
    for version in queryset:
        try:
            version.object_version.object.title
        except Exception: 
            continue
        
        infos = {'version': version,
                 'revision': version.revision,
                 'object': version.object_version.object,
                 'diff': None,
                 'language_code': 'en'}
        
        if version.content_type == project_translation_ct: # I4pProjectTranslation Type
            if project_translation_previous_version:
                infos['diff'] = fields_diff(project_translation_previous_version,
                                            version,
                                            VERSIONNED_FIELDS[project_translation_ct.model_class()])
            project_translation_previous_version = version

            try:
                instance = I4pProjectTranslation.objects.get(pk=version.object_version.object.pk)
                slug = instance.slug
                language_code = instance.language_code
            
            except I4pProjectTranslation.DoesNotExist:
                slug = None
                language_code = None
                
            infos['slug'] = slug
            infos['language_code'] = language_code or 'en'

        else: # I4pProject type:
            if parent_project_previous_version:
                infos['diff'] = fields_diff(parent_project_previous_version,
                                            version,
                                            VERSIONNED_FIELDS[parent_project_ct.model_class()])
            parent_project_previous_version = version

        if infos['diff']:
            history.append(infos)

    return history
