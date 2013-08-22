from django.views.generic.base import TemplateView
from apps.member.models import I4pProfile

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
Views for handling members
"""
from django.core.urlresolvers import reverse
from django.utils import translation
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.models import Site
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template

from userena import settings as userena_settings
from userena import views as userena_views
from userena.decorators import secure_required
from userena.forms import AuthenticationForm, ChangeEmailForm
from userena.forms import SignupForm, SignupFormOnlyEmail
from userena.utils import signin_redirect

from guardian.decorators import permission_required_or_403
from reversion.models import Version

from apps.project_sheet.utils import get_project_translations_from_parents
from apps.project_sheet.models import I4pProject

from .forms import I4PEditProfileForm, I4PSignupForm

@secure_required
def signup(request, signup_form,
           template_name='userena/signup_form.html', success_url=None,
           extra_context=None):
    """
    Custom version of userena's signup view that initialize profile language
    based on browser settings.
    """
    # If no usernames are wanted and the default form is used, fallback to the
    # default form that doesn't display to enter the username.
    if userena_settings.USERENA_WITHOUT_USERNAMES and (signup_form == SignupForm):
        signup_form = SignupFormOnlyEmail

    form = signup_form()

    if request.method == 'POST':
        form = signup_form(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            profile = user.get_profile()
            # Language
            profile.language = request.LANGUAGE_CODE
            profile.save()

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_signup_complete',
                                        kwargs={'username': user.username})

            # A new signed user should logout the old one.
            if request.user.is_authenticated():
                logout(request)
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)


def profile_detail(request, username):
    """
    Build a list of projects that matches, if possible, the language of the viewer.
    If not possible, fall back to english, and if not available, first language.
    """
    user = get_object_or_404(User, username__iexact=username)

    project_member_list = user.projects.all()

    project_translation_ct = ContentType.objects.get_for_model(I4pProject)

    # FIXME : UGLY AND DOESN'T WORK !
    version_ids = [int(id["object_id"]) for id in Version.objects.filter(content_type=project_translation_ct, revision__user=user).values('object_id').distinct()[:30]]
    project_contrib_list = I4pProject.objects.filter(id__in=version_ids)

    project_fan_list = I4pProject.objects.filter(fans__id=user.id)
    

    return userena_views.profile_detail(request,
                                        username,
                                        template_name='userena/profile_detail.html',
                                        extra_context={'project_member_list': project_member_list,
                                                       'project_contrib_list' : project_contrib_list,
                                                       'project_fan_list' : project_fan_list}
                                        )


@secure_required
def signin(request, 
           auth_form=AuthenticationForm,
           template_name='userena/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=signin_redirect, 
           extra_context=None):
    """
    Userena wrapper to signin a member.
    """
    extra_context = {'signup_form': I4PSignupForm()}
    
    response = userena_views.signin(request,
                                    auth_form=auth_form,
                                    template_name=template_name,
                                    redirect_field_name=REDIRECT_FIELD_NAME,
                                    redirect_signin_function=signin_redirect,
                                    extra_context=extra_context)
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        request.session['django_language'] = profile.language
    return response


@login_required
def profile_edit(request, username, edit_profile_form=I4PEditProfileForm,
                 template_name='userena/profile_form.html', success_url=None,
                 extra_context=None):
    """
    Custom version of userena's profile edit, with the three following forms:
     - Profile edition ;
     - Password update ;
     - Email update.
    """
    current_user = request.user

    requested_user = get_object_or_404(User,
                                       username__iexact=username)

    profile = requested_user.get_profile()

    if not current_user.has_perm('change_profile', profile):
        return HttpResponseForbidden()

    user_initial = {'first_name': requested_user.first_name,
                    'last_name': requested_user.last_name}

    if not extra_context:
        extra_context = {}

    # From userena. 
    form = edit_profile_form(instance=profile, initial=user_initial)

    # Also pass the password and email forms
    extra_context.update({'password_form': PasswordChangeForm(user=current_user),
                          'email_form': ChangeEmailForm(user=current_user),
                          'profile_form': form}
                         )


    if request.method == 'POST':
        form = edit_profile_form(request.POST, request.FILES, instance=profile,
                                 initial=user_initial)

        if form.is_valid():
            profile = form.save()

            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Your profile has been updated.'),
                                 fail_silently=True)

            if success_url:
                redirect_to = success_url
            else:
                translation.activate(profile.language)                                
                redirect_to = reverse('userena_profile_detail', kwargs={'username': username})

            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['profile'] = profile
    return direct_to_template(request,
                              template_name,
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
    

@login_required
def activate_success(request):
    """
    Userena doesn't allow to specify an activation success URL that takes a
    username. This wrapper view doesn't require a username. It gets the username
    from the request object and redirects to the profile edit screen URL ,which
    requires a username parameter.
    """
    return redirect(reverse('userena_profile_edit',
                            kwargs={'username': request.user.username}))
    
def direct_to_user_template(request, username, template_name,
                            extra_context=None):
    """
    Simple wrapper for Django's :func:`direct_to_template` view.

    This view is used when you want to show a template to a specific user. A
    wrapper for :func:`direct_to_template` where the template also has access to
    the user that is found with ``username``. For ex. used after signup,
    activation and confirmation of a new e-mail.

    :param username:
        String defining the username of the user that made the action.

    :param template_name:
        String defining the name of the template to use. Defaults to
        ``userena/signup_complete.html``.

    **Keyword arguments**

    ``extra_context``
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``account`` key is always the ``User``
        that completed the action.

    **Extra context**

    ``viewed_user``
        The currently :class:`User` that is viewed.

    """
    user = get_object_or_404(User, username__iexact=username)

    if not extra_context: extra_context = dict()
    extra_context['viewed_user'] = user
    extra_context['profile'] = user.get_profile()
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)


class MembersQuoteView(TemplateView):
    template_name = "member/quote.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        members = {}
        for member in I4pProfile.objects.filter(motto__isnull=False).exclude(motto__exact='').order_by("?"):
            members[member.get_full_name_or_username] = member.motto.replace('"', '').capitalize()
        context["members"] = members
        return context