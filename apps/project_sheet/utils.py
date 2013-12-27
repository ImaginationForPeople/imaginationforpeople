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
Toolkit for a project sheet management.
DeprecationWarning: Should now be replaced by Hvad calls
"""
import warnings

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import DatabaseError
from django.contrib.sites.models import Site

from .models import I4pProject, SiteTopic, VERSIONED_FIELDS
I4pProjectTranslation = I4pProject.objects.translations_model

from .filters import BestOfFilterForm, NameBaselineFilterForm, TopicFilterForm
from .filters import ProjectStatusFilterForm, ProjectProgressFilterForm, ProjectCountriesFilterForm
from .filters import ThemesFilterForm, WithMembersFilterForm, ProjectObjectiveFilterForm

deprecation_warning_text = "You should now use HVAD instead of this function."

def create_parent_project(topic_slug):
    """
    Create a parent project
    """
    warnings.warn(deprecation_warning_text, DeprecationWarning)
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
    warnings.warn(deprecation_warning_text, DeprecationWarning)    
    return I4pProjectTranslation.objects.get(language_code=language_code,
                                             slug=project_translation_slug)

def get_project_translation_by_any_translation_slug(project_translation_slug, prefered_language_code, site):
    """
    Get a translation of a given project, looking at slugs in any language
    """
    warnings.warn(deprecation_warning_text, DeprecationWarning)    
    try:
        project_translation = I4pProjectTranslation.objects.get(slug=project_translation_slug,
                                                                language_code=prefered_language_code,
                                                                master__site=site)
        return project_translation
    except I4pProjectTranslation.DoesNotExist:
        for lang_code, lang_name in settings.LANGUAGES:
             if lang_code != prefered_language_code:
                 try:
                     project_translation = I4pProjectTranslation.objects.get(slug=project_translation_slug,
                                                                             language_code=lang_code,
                                                                             master__site=site)
                     project_best_translation = get_project_translation_from_parent(project_translation.master,
                                                                                    prefered_language_code,
                                                                                    fallback_language=settings.LANGUAGE_CODE,
                                                                                    fallback_any=True)
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
    warnings.warn(deprecation_warning_text, DeprecationWarning)
    
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
    warnings.warn(deprecation_warning_text, DeprecationWarning)
    
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
    warnings.warn(deprecation_warning_text, DeprecationWarning)
    
    try:
        I4pProjectTranslation.objects.get(master=parent_project,
                                          language_code=language_code)
        raise DatabaseError('This translation already exist')
    except I4pProjectTranslation.DoesNotExist:
        pass

    if default_title:
        project_translation = I4pProjectTranslation.objects.create(master=parent_project,
                                                                   language_code=language_code,
                                                                   title=default_title)            
    else:
        project_translation = I4pProjectTranslation.objects.create(master=parent_project,
                                                                   language_code=language_code)

    return project_translation


def get_or_create_project_translation_by_slug(project_translation_slug, language_code, parent_project, default_title=None):
    """
    Create a project translation for the given language_code with the
    given slug.

    This version does need a parent. Beware: using it twice for
    the same language with a different slug can lead to duplicate
    projects.
    When possible, use the "_from_parent" version instead.
    """
    warnings.warn(deprecation_warning_text, DeprecationWarning)
    
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
    warnings.warn(deprecation_warning_text, DeprecationWarning)
    
    try:
        project_translation = get_project_translation_from_parent(parent_project, language_code)
    except I4pProjectTranslation.DoesNotExist:
        project_translation = create_project_translation(language_code=language_code,
                                                         parent_project=parent_project,
                                                         default_title=default_title)

    return project_translation

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
                                            VERSIONED_FIELDS[project_translation_ct.model_class().__name__])
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
                                            VERSIONED_FIELDS[parent_project_ct.model_class().__name__])
            parent_project_previous_version = version

        if infos['diff']:
            history.append(infos)

    return history

