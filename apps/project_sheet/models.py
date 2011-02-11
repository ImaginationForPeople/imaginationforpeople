# -*- coding: utf-8 -*-

# import stuff we need from django
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# import translation stuff
from mothertongue.models import MothertongueModelTranslate
from apps.member.models import I4pProfile

from tagging.fields import TagField
from autoslug.fields import AutoSlugField


class I4pProject(MothertongueModelTranslate):
    author = models.ForeignKey(I4pProfile, verbose_name=_("author"))
    ip_addr = models.IPAddressField(null=True, blank=True)
    created = models.DateField(_("creation date"), auto_now_add=True)
    location = models.CharField(_("location"), max_length=80)
    
    #TODO: add photos and videos list
    #see django-oembed, django-oembed-field and django-imagekit

    title = models.CharField(_("my project title"), max_length=80)
    slug = AutoSlugField(populate_from="title")
    baseline = models.CharField(_("my project\’s baseline"), max_length=180, null=True, blank=True)
    about_section = models.TextField(_("about the project"), null=True, blank=True)
    uniqueness_section = models.TextField(_("what is make it creative and unique"), null=True, blank=True)
    value_section = models.TextField(_("what is the experience social added value"), null=True, blank=True)
    scalability_section = models.TextField(_("how scalable it is"), null=True, blank=True)
    
    theme = TagField()
    
    translations = models.ManyToManyField("I4pProjectTranslation", blank=True, verbose_name=_("translations"))
    translation_set = "project_translation_set"
    translated_fields = ["title",
                         "baseline"
                         "slug",
                         "about_section",
                         "uniqueness_section",
                         "value_section",
                         "scalability_section"]

# chunks translations model
class I4pProjectTranslation(models.Model):
    i4p_project_instance = models.ForeignKey(I4pProject, verbose_name=_("project"))
    language = models.CharField(max_length=len(settings.LANGUAGES)-1, choices=settings.LANGUAGES[1:])
    
    title = models.CharField(_("title"), max_length=80)
    slug = AutoSlugField(populate_from="title")
    baseline = models.CharField(_("my project’s baseline"), max_length=180, null=True, blank=True)
    about_section = models.TextField(_("about the project"), null=True, blank=True)
    uniqueness_section = models.TextField(_("what is make it creative and unique"), null=True, blank=True)
    value_section = models.TextField(_("what is the experience social added value"), null=True, blank=True)
    scalability_section = models.TextField(_("how scalable it is"), null=True, blank=True)

    class Meta(object):
        unique_together = (("i4p_project_instance", "language"),)

    def __unicode__(self):
        return u"%s" % self.language
