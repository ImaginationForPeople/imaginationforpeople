from django.db import models
from django.utils.translation import ugettext_lazy as _
from userena.models import UserenaLanguageBaseProfile
from django_countries import CountryField
from apps.i4p_base.models import Location
from guardian.shortcuts import assign
from django.db.models.signals import post_save

class I4pProfile(UserenaLanguageBaseProfile):
    GENDER_TYPE = (
       ('M', _('male')),
       ('F', _('female'))
    )
    gender = models.CharField(max_length=1, choices=GENDER_TYPE, null=True, blank=True)
    motto = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    website = models.URLField(verbose_name=_('website'), verify_exists=True, max_length=200, blank=True)
    linkedin = models.URLField(verbose_name=_('linkedin'), verify_exists=True, max_length=200, blank=True)
    twitter = models.URLField(verbose_name=_('twitter'), verify_exists=True, max_length=200, blank=True)
    facebook = models.URLField(verbose_name=_('facebook'), verify_exists=True, max_length=200, blank=True)
    address = models.TextField(null=True, blank=True)
    country = CountryField(null=True, blank=True)
    location = models.OneToOneField(Location, verbose_name=_('location'), null=True, blank=True)


def assign_good_profile_perm(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        assign('change_profile', user, instance)
        assign('change_user', user, user)

post_save.connect(assign_good_profile_perm, I4pProfile)

def init_good_profile_perm():
    for profile in I4pProfile.objects.all():
        assign_good_profile_perm(I4pProfile, profile, True)
