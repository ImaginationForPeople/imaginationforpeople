"""
Views for handling members
"""
from httplib import HTTPConnection

from django.core.mail import mail_admins
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404

from userena import views as userena_views
from userena.decorators import secure_required
from userena.forms import AuthenticationForm, ChangeEmailForm
from userena.utils import signin_redirect, get_profile_model

from guardian.decorators import permission_required_or_403
from reversion.models import Version

from apps.project_sheet.utils import get_project_translations_from_parents
from apps.project_sheet.models import I4pProjectTranslation

from .forms import I4PEditProfileForm


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

    # FIXME : UGLY AND DOESN'T WORK !
    version_ids = [int(id["object_id"]) for id in Version.objects.filter(content_type=project_translation_ct, revision__user=user).values('object_id').distinct()[:30]]
    project_contrib_list = I4pProjectTranslation.objects.filter(id__in=version_ids)

    return userena_views.profile_detail(request,
                                        username,
                                        template_name='userena/profile_detail.html',
                                        extra_context={'project_translation_list': project_translation_list,
                                                       'project_contrib_list' : project_contrib_list}
                                        )


@secure_required
def signin(request, 
           auth_form=AuthenticationForm,
           template_name='userena/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=signin_redirect, 
           extra_context=None):
    """
    Userena wrapper to signin a member. Also login the user on the
    wiki (alpha.) by calling a remote view and grabbing the PHPSESSID
    cookie.
    """
    
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
                # We don't care if it was not possible to login the user on the wiki
                mail_admins(subject='YesWiki login error',
                            message="%s" % e)

    return response




@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def profile_edit(request, username, edit_profile_form=I4PEditProfileForm,
                 template_name='userena/profile_form.html', success_url=None,
                 extra_context=None):
    """
    Custom version of userena's profile edit, with the three following forms:
     - Profile edition ;
     - Password update ;
     - Email update.
    """
    user = get_object_or_404(User,
                             username__iexact=username)

    profile = user.get_profile()

    user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}

    if not extra_context:
        extra_context = {}

    # Also pass the password and email forms
    extra_context.update({'password_form': PasswordChangeForm(user=request.user),
                          'email_form': ChangeEmailForm(user=request.user),
                          'profile_form': I4PEditProfileForm(instance=profile, initial=user_initial)}
                         )


    return userena_views.profile_edit(request=request,
                                      username=username,
                                      edit_profile_form=edit_profile_form,
                                      template_name=template_name,
                                      success_url=success_url,
                                      extra_context=extra_context)
    


@secure_required
@permission_required_or_403('change_user', (User, 'username', 'username'))
def password_change(request, username, template_name='userena/password_form.html',
                    pass_form=PasswordChangeForm, success_url=None, extra_context=None):

    user = get_object_or_404(User,
                             username__iexact=username)

    profile = user.get_profile()

    user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}

    if not extra_context:
        extra_context = {}

    # Also pass the password and email forms
    extra_context.update({'password_form': PasswordChangeForm(user=request.user),
                          'email_form': ChangeEmailForm(user=request.user),
                          'profile_form': I4PEditProfileForm(instance=profile, initial=user_initial)}
                         )

    return userena_views.password_change(request=request, 
                                         username=username, 
                                         template_name=template_name,
                                         pass_form=pass_form, 
                                         success_url=success_url, 
                                         extra_context=extra_context)


@secure_required
@permission_required_or_403('change_user', (User, 'username', 'username'))
def email_change(request, username, form=ChangeEmailForm,
                 template_name='userena/email_form.html', success_url=None,
                 extra_context=None):

    user = get_object_or_404(User,
                             username__iexact=username)

    profile = user.get_profile()

    user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}

    if not extra_context:
        extra_context = {}

    # Also pass the password and email forms
    extra_context.update({'password_form': PasswordChangeForm(user=request.user),
                          'email_form': ChangeEmailForm(user=request.user),
                          'profile_form': I4PEditProfileForm(instance=profile, initial=user_initial)
                          })

    return userena_views.email_change(request=request,
                                      username=username,
                                      form=form,
                                      template_name=template_name,
                                      success_url=success_url,
                                      extra_context=extra_context)
    
