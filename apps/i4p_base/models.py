# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_countries import CountryField

class Location(models.Model):
    """
    A generic location model designed to be used to localize any object
    """
    lat = models.FloatField(verbose_name=_('latitude'),
                            null=True, blank=True)
    
    lon = models.FloatField(verbose_name=_('longitude'),
                            null=True, blank=True)

    country = CountryField(verbose_name=_('country'),
                           null=True, blank=True)

    address = models.TextField(verbose_name=_('address'),
                               null=True, blank=True)




