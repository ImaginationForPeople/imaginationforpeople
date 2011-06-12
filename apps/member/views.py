from django.utils import translation
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from userena import views as userena_views


from apps.project_sheet.utils import get_project_translation_from_parent
from reversion.models import Version
from django.contrib.contenttypes.models import ContentType
from apps.project_sheet.models import I4pProjectTranslation

def profile_detail(request, username):
    """
    Build a list of projects that matches, if possible, the language of the viewer.
    If not possible, fall back to english, and if not available, first language.
    """
    user = get_object_or_404(User, username__iexact=username)

    project_translation_list = [get_project_translation_from_parent(project, 
                                                                    language_code=translation.get_language(),
                                                                    fallback_language='en', 
                                                                    fallback_any=True
                                                                    )
                                for project
                                in user.projects.all().distinct()[:3]
                                ]

    project_translation_ct = ContentType.objects.get_for_model(I4pProjectTranslation)
    project_contrib_list = I4pProjectTranslation.objects.filter(id__in=Version.objects.filter(content_type=project_translation_ct, revision__user=user).values_list('object_id', flat=True))

    return userena_views.profile_detail(request,
                                        username,
                                        template_name='userena/profile_detail.html',
                                        extra_context={'project_translation_list': project_translation_list,
                                                       'project_contrib_list' : project_contrib_list}
                                        )
