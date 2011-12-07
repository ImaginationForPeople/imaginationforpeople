#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views as auth_views

from userena import views as userena_views
from userena import settings as userena_settings

from apps.member.forms import I4PSignupForm

import views as member_views

urlpatterns = patterns('',
                       # Signup, signin and signout
                       url(r'^signup/$',
                           userena_views.signup,
                           {'signup_form' : I4PSignupForm},
                           name='userena_signup'),
                       url(r'^signin/$',
                           member_views.signin,
                           name='userena_signin'),
                       url(r'^signout/$',
                           auth_views.logout,
                           {'template_name': 'userena/signout.html'},
                           name='userena_signout'),

                       # Reset password
                       url(r'^password/reset/$',
                           auth_views.password_reset,
                           {'template_name': 'userena/password_reset_form.html',
                            'email_template_name': 'userena/emails/password_reset_message.txt'},
                           name='userena_password_reset'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           {'template_name': 'userena/password_reset_done.html'},
                           name='userena_password_reset_done'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           {'template_name': 'userena/password_reset_confirm_form.html'},
                           name='userena_password_reset_confirm'),
                       url(r'^password/reset/confirm/complete/$',
                           auth_views.password_reset_complete,
                           {'template_name': 'userena/password_reset_complete.html'}),

                       # Signup
                       url(r'^(?P<username>\w+)/signup/complete/$',
                           userena_views.direct_to_user_template,
                           {'template_name': 'userena/signup_complete.html',
                            'extra_context': {'userena_activation_days': userena_settings.USERENA_ACTIVATION_DAYS}},
                           name='userena_signup_complete'),

                       # Activate
                       url(r'^(?P<username>\w+)/activate/complete/$',
                           userena_views.direct_to_user_template,
                           {'template_name': 'userena/activate_complete.html'},
                           name='userena_activate_complete'),
                       url(r'^(?P<username>\w+)/activate/(?P<activation_key>\w+)/$',
                           userena_views.activate,
                           {'success_url': '/member/activate_success'},
                           name='userena_activate'),
                       url(r'^activate_success/?$',
                           # This redirects to userena_profile_edit
                           member_views.activate_success),

                       # Change email and confirm it
                       url(r'^(?P<username>\w+)/email/$',
                           member_views.email_change,
                           name='userena_email_change'),
                       url(r'^(?P<username>\w+)/email/complete/$',
                           userena_views.direct_to_user_template,
                           {'template_name': 'userena/email_change_complete.html'},
                           name='userena_email_change_complete'),
                       url(r'^(?P<username>\w+)/confirm-email/complete/$',
                           userena_views.direct_to_user_template,
                           {'template_name': 'userena/email_confirm_complete.html'},
                           name='userena_email_confirm_complete'),
                       url(r'^(?P<username>\w+)/confirm-email/(?P<confirmation_key>\w+)/$',
                           userena_views.email_confirm,
                           name='userena_email_confirm'),

                       # Disabled account
                       url(r'^(?P<username>\w+)/disabled/$',
                           userena_views.direct_to_user_template,
                           {'template_name': 'userena/disabled.html'},
                           name='userena_disabled'),

                       # Change password
                       url(r'^(?P<username>\w+)/password/$',
                           member_views.password_change,
                           name='userena_password_change'),
                       url(r'^(?P<username>\w+)/password/complete/$',
                           userena_views.direct_to_user_template,
                           {'template_name': 'userena/password_complete.html'},
                           name='userena_password_change_complete'),

                       # Edit profile
                       url(r'^(?P<username>\w+)/edit/$',
                           member_views.profile_edit,
                           name='userena_profile_edit'),

                       # View profiles
                       url(r'^(?P<username>\w+)/$',
                           member_views.profile_detail,
                           name='userena_profile_detail'),
                       url(r'^page/(?P<page>[0-9]+)/$',
                           userena_views.profile_list,
                           name='userena_profile_list_paginated'),
                       url(r'^$',
                           userena_views.profile_list,
                           name='userena_profile_list'),
                       )






