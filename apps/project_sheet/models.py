# -*- coding: utf-8 -*-

# import stuff we need from django
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from autoslug.fields import AutoSlugField
from imagekit.models import ImageModel
from tagging.fields import TagField
from licenses.fields import LicenseField
import reversion

from apps.member.models import I4pProfile

from apps.i4p_base.models import Address

class ProjectReference(models.Model):
    desc = models.CharField(_("description"), max_length=300)
    
class I4pProject(models.Model):
    """
    Root object for a project. Holds only shared data
    """

    OBJECTIVE_CHOICES = [
        ('EDUC', _('Educate')),
        ('CONT', _('Contribute')),
        ]

    author = models.ForeignKey(I4pProfile, verbose_name=_("author"), null=True, blank=True)
    ip_addr = models.IPAddressField(null=True, blank=True)
    
    created = models.DateField(_("creation date"), auto_now_add=True)
    location = models.CharField(_("location"), max_length=80, null=True, blank=True)

    objective = models.CharField(verbose_name=_('objective'),
                                 max_length=4, choices=OBJECTIVE_CHOICES,
                                 null=True, blank=True)

    website = models.URLField(verbose_name=_('website'),
                              verify_exists=True,
                              max_length=200,
                              null=True,
                              blank=True)

    project_leader_info = models.TextField(verbose_name=_('project leader information'),
                                           null=True, blank=True)

    location = models.OneToOneField(Address,
                                    verbose_name=_('location'),
                                    null=True, blank=True
                                    )
    
    references = models.ManyToManyField(ProjectReference, null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('project_sheet-show', (self.slug,))

    def __unicode__(self):
        return u"Parent project %d" % self.id


class I4pProjectTranslation(models.Model):
    """
    A translation of a project
    """

    class Meta:
        unique_together = ('project', 'language_code', 'slug')

    project = models.ForeignKey(I4pProject, related_name='translations')

    language_code = models.CharField(_('language'),
                                     max_length=6,
                                     choices=settings.LANGUAGES)

    title = models.CharField(_("title"), max_length=80,
                             default=_("My Project Title"))
    slug = AutoSlugField(populate_from="title",
                         always_update=True,
                         unique_with=['language_code'])

    baseline = models.CharField(_("my project baseline"), max_length=180, null=True, blank=True, default=_("My baseline"))
    about_section = models.TextField(_("about the project"), null=True, blank=True)
    uniqueness_section = models.TextField(_("what is make it creative and unique"), null=True, blank=True)
    value_section = models.TextField(_("what is the experience social added value"), null=True, blank=True)
    scalability_section = models.TextField(_("how scalable it is"), null=True, blank=True)
    
    themes = TagField(_("Themes of the project"), null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('project_sheet-show', (self.slug,))

    def __unicode__(self):
        return u"Translation of '%s' in '%s' : %s" % (self.project, self.language_code, self.slug)


def get_projectpicture_path(aProjectPicture, filename):
    dst = 'uploads/projects/%d/pictures/%s' % (aProjectPicture.project.id, filename)
    return dst

class ProjectPicture(ImageModel):
    name = models.CharField(max_length=100)
    original_image = models.ImageField(upload_to=get_projectpicture_path)
    project = models.ForeignKey(I4pProject, related_name="pictures")
    created = models.DateField(_("creation date"), auto_now_add=True)
    desc = models.CharField(_("description"), max_length=150, null=True, blank=True)
    author = models.CharField(_("author"), max_length=150, null=True, blank=True)
    source = models.CharField(_("source"), max_length=150, null=True, blank=True)
    license = LicenseField(required = False)

    class IKOptions:
        spec_module = 'apps.project_sheet.project_pictures_specs'
        image_field = 'original_image'


class ProjectVideo(models.Model):
    video_url = models.URLField()
    project = models.ForeignKey(I4pProject, related_name="videos")
    

# Reversions
reversion.register(I4pProject)
reversion.register(I4pProjectTranslation)
