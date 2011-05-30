from django.utils import translation

from .models import I4pProject, I4pProjectTranslation

def create_parent_project():
    """
    Create a parent project
    """
    return I4pProject.objects.create()

def get_or_create_project(request, project_slug):
    """
    Get or create a project
    If a creation is needed, only the base language version is created
    """
    try:
        project = get_project(project_slug)
    except I4pProject.DoesNotExist:
        project = create_project(request)

    return project


def get_project_translation_by_slug(project_translation_slug, language_code):
    """
    Get a translation of a given project
    """
    return I4pProjectTranslation.objects.get(language_code=language_code,
                                             slug=project_translation_slug)


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
                project_translation = parent.translations.get(language_code=language_code)
            except I4pProjectTranslation.DoesNotExist, e:
                if fallback_any:
                    project_translation = parent.translations.all()[0]
                else:
                    raise e
        else:
            raise e

    return project_translation

def create_project_translation(language_code, parent_project=None, default_title=None):
    """
    Create a translation of a project.
    If needed, create a parent project.
    """
    if not parent_project:
        parent_project = create_parent_project()

    if default_title:
        project_translation = I4pProjectTranslation.objects.create(project=parent_project,
                                                                   language_code=language_code,
                                                                   title=default_title)
    else:
        project_translation = I4pProjectTranslation.objects.create(project=parent_project,
                                                                   language_code=language_code)

    return project_translation


def get_or_create_project_translation_by_slug(project_translation_slug, language_code, parent_project=None, default_title=None):
    """
    Create a project translation for the given language_code with the
    given slug.

    This version does not need a parent. Beware: using it twice for
    the same language with a different slug can lead to duplicate
    projects.
    When possible, use the "_from_parent" version instead.

    It can create the parent project if needed.
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








