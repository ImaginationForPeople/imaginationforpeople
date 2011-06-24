from django.utils import translation
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import get_object_or_404
from django.test.client import Client

from userena import views as userena_views
from userena.decorators import secure_required
from userena.forms import AuthenticationForm
from userena.utils import signin_redirect

from apps.project_sheet.utils import get_project_translations_from_parents
from reversion.models import Version
from django.contrib.contenttypes.models import ContentType
from apps.project_sheet.models import I4pProjectTranslation

def profile_detail(request, username):
    """
    Build a list of projects that matches, if possible, the language of the viewer.
    If not possible, fall back to english, and if not available, first language.
    """
    user = get_object_or_404(User, username__iexact=username)

    project_translation_list = get_project_translations_from_parents(user.projects.all().distinct()[:3],
                                                                     language_code=translation.get_language()
                                                                     )

    project_translation_ct = ContentType.objects.get_for_model(I4pProjectTranslation)
    project_contrib_list = I4pProjectTranslation.objects.filter(id__in=Version.objects.filter(content_type=project_translation_ct, revision__user=user).values_list('object_id', flat=True))

    return userena_views.profile_detail(request,
                                        username,
                                        template_name='userena/profile_detail.html',
                                        extra_context={'project_translation_list': project_translation_list,
                                                       'project_contrib_list' : project_contrib_list}
                                        )


import urllib2
import cookielib
from httplib import HTTPConnection

@secure_required
def signin(request, 
           auth_form=AuthenticationForm,
           template_name='userena/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=signin_redirect, 
           extra_context=None):

    
    response = userena_views.signin(request,
                                    auth_form=auth_form,
                                    template_name=template_name,
                                    redirect_field_name=REDIRECT_FIELD_NAME,
                                    redirect_signin_function=signin_redirect,
                                    extra_context=extra_context)


    if request.method == 'POST':
        form = auth_form(request.POST)
        if form.is_valid():
            user = form.cleaned_data['identification']
            password = form.cleaned_data['password']

            # Temp fix to auth on Alpha
            try:
                conn = HTTPConnection('imaginationforpeople.org', timeout=5)
                conn.request('GET', '/wiki/jrest/User/%s/%s' % (user, password))

                res = conn.getresponse()
                cookies = res.getheader("set-cookie")   
                
                if res.status == 200:
                    name, value = cookies.split(";")[0].split("=")
                    response.set_cookie(name, value=value, domain=".imaginationforpeople.org")

            except Exception, e:
                pass


    return response


    
