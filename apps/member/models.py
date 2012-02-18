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
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import mail_managers, send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django_countries import CountryField
from guardian.shortcuts import assign
from social_auth.backends.google import GoogleOAuthBackend
from social_auth.backends.contrib.linkedin import LinkedinBackend
from social_auth.signals import socialauth_registered
from userena.managers import ASSIGNED_PERMISSIONS
from userena.models import UserenaLanguageBaseProfile
from userena.signals import activation_complete
from userena.utils import get_profile_model
from userena.contrib.umessages.models import MessageRecipient
from userena.utils import get_protocol

from apps.i4p_base.models import Location, I4P_COUNTRIES

from .utils import fix_username
from .social import fetch_profile_data


class I4pProfile(UserenaLanguageBaseProfile):
    """
    Userena Profile with language switch
    """
    GENDER_TYPE = (
       ('M', _('male')),
       ('F', _('female'))
    )
    user = models.ForeignKey(User)
    gender = models.CharField(max_length=1, choices=GENDER_TYPE, null=True, blank=True)
    motto = models.TextField(_("motto"), null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    birthday = models.DateField(_("birthday"), null=True, blank=True)
    website = models.URLField(verbose_name=_('website'), verify_exists=True, max_length=200, blank=True)
    linkedin = models.URLField(verbose_name=_('linkedin'), verify_exists=True, max_length=200, blank=True)
    twitter = models.URLField(verbose_name=_('twitter'), verify_exists=True, max_length=200, blank=True)
    facebook = models.URLField(verbose_name=_('facebook'), verify_exists=True, max_length=200, blank=True)
    address = models.TextField(_("address"), null=True, blank=True)
    country = CountryField(_("country"), null=True, blank=True, choices=I4P_COUNTRIES)

    #FIXME:  USELESS ???
    location = models.OneToOneField(Location, verbose_name=_('location'), null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('userena_profile_detail', [self.user.username])


@receiver(activation_complete, dispatch_uid='email-on-new-user')
def email_managers_on_account_activation(sender, user, **kwargs):
    body = render_to_string('member/emails/new_user.txt', {'user': user})
    mail_managers(subject=_(u'New user registered'), message=body)
        

@receiver(socialauth_registered,
        dispatch_uid="apps.member.models.socialauth_registered_handler")
def socialauth_registered_handler(sender, user, response, details, **kwargs):
    """
    Called when user registers for the first time using social auth
    """
    # Create user profile
    profile_model = get_profile_model()
    new_profile = profile_model(user=user)
    new_profile.save()

    # Give permissions to view and change profile
    for perm in ASSIGNED_PERMISSIONS['profile']:
        assign(perm[0], user, new_profile)

    # Give permissions to view and change itself
    for perm in ASSIGNED_PERMISSIONS['user']:
        assign(perm[0], user, user)

    # Try to get profile details
    fetch_profile_data(sender, new_profile, response)

    return True


@receiver(post_save, sender=MessageRecipient,
        dispatch_uid="apps.member.models.send_message_notification")
def send_message_notification(sender, instance, **kwargs):
    """
    Send email when user receives a new message. This email contains the full text
    and a link to read it online.

    We trigger this when a MessageRecipient is saved and not when a Message is
    saved because umessages first saves a message and then adds its recipients,
    so when a Message is saved, it doesn't yet have a list of recipients.
    """

    if not instance.user.email:
        # Email can be missing for users registered with Twitter
        # or LinkedIn
        return

    params = {
        'sender': instance.message.sender.username,
        'body': instance.message.body,
        }
    message_url_path = reverse('userena_umessages_detail',
                               kwargs={'username': params['sender']})
    params['message_url'] = "%s://%s%s" % (
            get_protocol(),
            Site.objects.get_current(), 
            message_url_path)

    subject = _(u'Message from %(sender)s') % params
    message = render_to_string('umessages/message_notification.txt', params)
    recipient = instance.user.email

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])


