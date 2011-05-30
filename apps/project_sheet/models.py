# -*- coding: utf-8 -*-

# import stuff we need from django
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from autoslug.fields import AutoSlugField
from imagekit.models import ImageModel
from tagging.fields import TagField
from licenses.fields import LicenseField
import reversion

from apps.member.models import I4pProfile

from apps.i4p_base.models import Location

# Add Introspector for south: django-licenses field
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^licenses\.fields\.LicenseField"])

class ProjectReference(models.Model):
    desc = models.CharField(_("description"), max_length=300, help_text=_("Insert your reference here (URL, books, etc)"))

class I4pProject(models.Model):
    """
    Root object for a project. Holds only shared data
    """

    OBJECTIVE_CHOICES = [
        ('', _('-----')),
        ('EDUC', _('Educate')),
        ('CONT', _('Contribute')),
        ]

    STATUS_CHOICES = [
        ('IDEA', _('Concept')),
        ('BEGIN', _('Starting')),
        ('WIP', _('In development')),
        ('END', _('Finished')),
    ]
    author = models.ForeignKey(I4pProfile, verbose_name=_("author"), null=True, blank=True)
    ip_addr = models.IPAddressField(null=True, blank=True)

    members = models.ManyToManyField(User,
                                     verbose_name=_("members"),
                                     through='ProjectMember',
                                     related_name='projects',
                                     )

    best_of = models.BooleanField(verbose_name=_('best of'), default=False)

    created = models.DateField(_("creation date"), auto_now_add=True)

    objective = models.CharField(verbose_name=_('objective'),
                                 max_length=4, choices=OBJECTIVE_CHOICES,
                                 null=True, blank=True)

    website = models.URLField(verbose_name=_('website'),
                              verify_exists=True,
                              max_length=200,
                              null=True,
                              blank=True)

    status = models.CharField(verbose_name=_('status'),
                              max_length=5, choices=STATUS_CHOICES, default="IDEA",
                              null=True, blank=True)

    project_leader_info = models.TextField(verbose_name=_('project leader information'),
                                           null=True, blank=True)

    location = models.OneToOneField(Location,
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

    PROGRESS_CHOICES = [
        ("EDITING", _("In edition")),
        ("FULL", _("Complete")),
    ]
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

    completion_progress = models.CharField(verbose_name=_('status'),
                                max_length=5, choices=PROGRESS_CHOICES, default="EDITING",
                                null=True, blank=True)

    baseline = models.CharField(_("one line description"), max_length=180, null=True, blank=True, default=_("One line description"))
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
    license = LicenseField(verbose_name=_("license"),
                           required=False)

    class IKOptions:
        spec_module = 'apps.project_sheet.project_pictures_specs'
        image_field = 'original_image'


class ProjectVideo(models.Model):
    video_url = models.URLField()
    project = models.ForeignKey(I4pProject, related_name="videos")

class ProjectMember(models.Model):
    class Meta:
        unique_together = ('project', 'user')

    project = models.ForeignKey(I4pProject, related_name="detailed_members")
    user = models.ForeignKey(User, related_name="project_memberships")

    role = models.CharField(verbose_name=_("role"),
                            max_length=100,
                            blank=True,
                            null=True)

    comment = models.TextField(verbose_name=_("comment"),
                               blank=False,
                               null=True)

    def __unicode__(self):
        return "%s - %s" % (self.project, self.user)


# Reversions
VERSIONNED_FIELDS = {
    I4pProject : ['author', 'objective', 'website', 'project_leader_info', 'location'],
    I4pProjectTranslation : ['title', 'baseline', 'about_section', 'uniqueness_section', 'value_section', 'scalability_section', 'themes']
}

for model, fields in VERSIONNED_FIELDS.iteritems():
        reversion.register(model, fields=fields)

