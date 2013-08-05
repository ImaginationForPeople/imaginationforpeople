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

from askbot.models.profile import AskbotBaseProfile, add_missing_subscriptions
from django_countries import CountryField
from social_auth.signals import socialauth_registered
from userena.models import UserenaLanguageBaseProfile
from userena.signals import activation_complete
from userena.contrib.umessages.models import MessageRecipient
from userena.utils import get_protocol

from apps.i4p_base.models import Location, I4P_COUNTRIES

from .social import fetch_profile_data

from tastypie.models import create_api_key 

models.signals.post_save.connect(create_api_key, sender=User)

class I4pProfile(UserenaLanguageBaseProfile, AskbotBaseProfile):
    """
    Userena Profile with language switch
    """
    GENDER_TYPE = (
       ('M', _('male')),
       ('F', _('female'))
    )
    user = models.ForeignKey(User, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER_TYPE, null=True, blank=True)
    motto = models.TextField(_("motto"), null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    birthday = models.DateField(_("birthday"), null=True, blank=True)
    website = models.URLField(verbose_name=_('website'), max_length=200, blank=True)
    linkedin = models.URLField(verbose_name=_('linkedin'),  max_length=200, blank=True)
    twitter = models.URLField(verbose_name=_('twitter'), max_length=200, blank=True)
    facebook = models.URLField(verbose_name=_('facebook'), max_length=200, blank=True)
    address = models.TextField(_("address"), null=True, blank=True)
    country = CountryField(_("country"), null=True, blank=True, choices=I4P_COUNTRIES)

    registration_site = models.ForeignKey(Site, verbose_name=_("registration site"), default=1)

    # FIXME:  USELESS ???
    location = models.OneToOneField(Location, verbose_name=_('location'), null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('userena_profile_detail', [self.user.username])

post_save.connect(add_missing_subscriptions, sender=I4pProfile)

@receiver(post_save, sender=I4pProfile, dispatch_uid='set-registration-site-on-profile')
def set_registration_site_on_profile(sender, instance, created, **kwargs):
    if created:
        instance.registration_site = Site.objects.get_current()
        instance.save()

@receiver(activation_complete, dispatch_uid='email-on-new-user')
def email_managers_on_account_activation(sender, user, **kwargs):
    body = render_to_string('member/emails/new_user.txt', {'user': user})
    mail_managers(subject=_(u'New user registered'), message=body)
        

@receiver(socialauth_registered,
          dispatch_uid='apps.member.models.socialauth_registered_handler')
def socialauth_registered_handler(sender, user, response, details, **kwargs):
    """
    Called when user registers for the first time using social auth
    """
    # Create user profile
    profile = user.get_profile()

    # Try to get profile details
    fetch_profile_data(sender, profile, response)

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

    subject = _(u'New message from %(sender)s on Imagination For People') % params
    message = render_to_string('umessages/message_notification.txt', params)
    recipient = instance.user.email

    # XXX Resets the Content-Transfer-Encoding in email header
    # Avoids bad encoding of UTF-8 body
    # See https://code.djangoproject.com/ticket/3472
    from email import Charset
    Charset.add_charset('utf-8', Charset.SHORTEST, 'utf-8', 'utf-8')

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
