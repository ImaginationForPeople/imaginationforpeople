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

from imagekit.models import ImageModel


class I4pProject(MothertongueModelTranslate):
    author = models.ForeignKey(I4pProfile, verbose_name=_("author"), null=True, blank=True)
    ip_addr = models.IPAddressField(null=True, blank=True)
    
    created = models.DateField(_("creation date"), auto_now_add=True)
    location = models.CharField(_("location"), max_length=80, null=True, blank=True)

    title = models.CharField(_("my project title"), max_length=80, default=_("my project title"))
    slug = AutoSlugField(populate_from="title", unique=True, always_update=True)
    baseline = models.CharField(_("my project baseline"), max_length=180, default=_("my project baseline"))
    about_section = models.TextField(_("about the project"), null=True, blank=True)
    uniqueness_section = models.TextField(_("what is make it creative and unique"), null=True, blank=True)
    value_section = models.TextField(_("what is the experience social added value"), null=True, blank=True)
    scalability_section = models.TextField(_("how scalable it is"), null=True, blank=True)
    
    OBJECTIVE_CHOICES = [
        ('EDUC', _('Educate')),
        ('CONT', _('Contribute')),
        ]

    objective = models.CharField(verbose_name=_('Objective'),
                                 max_length=4, choices=OBJECTIVE_CHOICES)

    themes = TagField()
    
    translations = models.ManyToManyField("I4pProjectTranslation", blank=True, verbose_name=_("translations"))
    translation_set = "project_translation_set"
    translated_fields = ["title",
                         "baseline"
                         "slug",
                         "about_section",
                         "uniqueness_section",
                         "value_section",
                         "scalability_section"]

    @models.permalink
    def get_absolute_url(self):
        return ('project_sheet-show', (self.slug,))

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


def get_projectpicture_path(aProjectPicture, filename):
    dst = 'uploads/projects/%d/pictures/%s' % (aProjectPicture.project.id, filename)
    return dst

class ProjectPicture(ImageModel):
    name = models.CharField(max_length=100)
    original_image = models.ImageField(upload_to=get_projectpicture_path)
    project = models.ForeignKey(I4pProject, related_name="pictures")

    class IKOptions:
        spec_module = 'apps.project_sheet.project_pictures_specs'
        image_field = 'original_image'
        
class ProjectVideo(models.Model):
    video_url = models.URLField()
    project = models.ForeignKey(I4pProject, related_name="videos")
    



