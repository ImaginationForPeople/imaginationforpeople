from django.db import models
from django.utils.translation import ugettext_lazy as _
from userena.models import UserenaLanguageBaseProfile
from django_countries import CountryField
from apps.i4p_base.models import Location

class I4pProfile(UserenaLanguageBaseProfile):
    #From UserenaLanguageBaseProfile.user
    #    - first_name
    #    - last_name
    #    - email
    #    - password
    #From UserenaLanguageBaseProfile
    #    - user language
    #    - mugshot
    #    - privacy (profile visibility)

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




