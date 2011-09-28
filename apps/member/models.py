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
from django.core.mail import mail_managers
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django_countries import CountryField
from guardian.shortcuts import assign
from userena.models import UserenaLanguageBaseProfile
from userena.signals import activation_complete

from apps.i4p_base.models import Location, I4P_COUNTRIES

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
    motto = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    website = models.URLField(verbose_name=_('website'), verify_exists=True, max_length=200, blank=True)
    linkedin = models.URLField(verbose_name=_('linkedin'), verify_exists=True, max_length=200, blank=True)
    twitter = models.URLField(verbose_name=_('twitter'), verify_exists=True, max_length=200, blank=True)
    facebook = models.URLField(verbose_name=_('facebook'), verify_exists=True, max_length=200, blank=True)
    address = models.TextField(null=True, blank=True)
    country = CountryField(null=True, blank=True, choices=I4P_COUNTRIES)

    #FIXME:  USELESS ???
    location = models.OneToOneField(Location, verbose_name=_('location'), null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('userena_profile_detail', [self.user.username])

@receiver(activation_complete, dispatch_uid='email-on-new-user')
def email_managers_on_account_activation(sender, user, **kwargs):
    body = render_to_string('member/emails/new_user.txt', {'user': user})
    mail_managers(subject=_(u'New user registered'), message=body)
        

# XXX: userena should be enough
# def assign_good_profile_perm(sender, instance, created, **kwargs):
#     if created:
#         user = instance.user
#         assign('change_profile', user, instance)
#         assign('change_user', user, user)

# post_save.connect(assign_good_profile_perm, I4pProfile)

# def init_good_profile_perm():
#     for profile in I4pProfile.objects.all():
#         assign_good_profile_perm(I4pProfile, profile, True)
