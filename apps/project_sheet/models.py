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
# -*- coding: utf-8 -*-
"""
Models for Project Sheet
"""
import uuid
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.core.mail import mail_managers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from autoslug.fields import AutoSlugField
from imagekit.models import ImageModel
from licenses.fields import LicenseField
from localeurl.models import reverse
from nani.models import TranslatableModel, TranslatedFields
import reversion
from reversion.models import Version
from south.modelsinspector import add_introspection_rules
from south.modelsinspector import add_ignored_fields
from tagging.fields import TagField

from apps.member.models import I4pProfile
from apps.i4p_base.models import Location

# Add Introspector for south: django-licenses field
add_introspection_rules([], ["^licenses\.fields\.LicenseField"])

class ProjectReference(models.Model):
    """
    A reference, such as a book or URL, for a Project Sheet
    """
    desc = models.CharField(_("description"), max_length=300, help_text=_("Insert your reference here (URL, books, etc)"))

class Objective(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(max_length=255)
    )

    def __unicode__(self):
        return self.safe_translation_getter('name', 'Objective: %s' % self.pk)

class Topic(TranslatableModel):
    """
    A topic is a project type, aka. Template.
    """
    untranslated_name = models.CharField(_("Untranslated name"), max_length=128, default='New topic')
    slug = AutoSlugField(populate_from="untranslated_name",
                         always_update=True,
                         unique=True)
    translations = TranslatedFields(
        label = models.CharField("Label", max_length=512)
    )

    def __unicode__(self):
        return self.untranslated_name

class SiteTopic(models.Model):
    """
    Topics allowed on a given site
    """
    site = models.ForeignKey(Site, related_name='site_topics')
    topic = models.ForeignKey(Topic, related_name='site_topics')
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = (('site', 'topic'),)
    
    def __unicode__(self):
        return '%s & %s' % (self.site, self.topic) 

class I4pProject(models.Model):
    """
    Root object for a project. Holds only shared data
    """

    STATUS_CHOICES = [
        ('IDEA', _('Concept')),
        ('BEGIN', _('Starting')),
        ('WIP', _('In development')),
        ('END', _('Mature')),
    ]
    author = models.ForeignKey(I4pProfile, verbose_name=_("author"), null=True, blank=True)
    ip_addr = models.CharField(max_length=15, null=True, blank=True)

    members = models.ManyToManyField(User,
                                     verbose_name=_("members"),
                                     through='ProjectMember',
                                     related_name='projects',
                                     )

    best_of = models.BooleanField(verbose_name=_('best of'), default=False)

    created = models.DateTimeField(verbose_name=_("creation date"),
                                   auto_now_add=True)

    objectives = models.ManyToManyField(Objective, verbose_name=_('objectives'), null=True, blank=True)

    website = models.URLField(verbose_name=_('website'),
                              verify_exists=False,
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

    topics = models.ManyToManyField(SiteTopic, verbose_name=_('topics'))

    # dynamicsites
    site = models.ManyToManyField(Site, help_text=_('The sites that the project sheet is accessible at.'), verbose_name=_("sites"))
    objects = models.Manager()
    on_site = CurrentSiteManager()
    
    add_ignored_fields(["^dynamicsites\.fields\.FolderNameField"])
    add_ignored_fields(["^dynamicsites\.fields\.SubdomainListField"])
    
    
    
    def __unicode__(self):
        res = u"Parent project %d" % self.id
        if self.translations.all().count():
            res = "%s (%s)" % (res,
                               self.translations.all()[0].slug)

        return res


    def get_absolute_url(self):
        # Don't move this, or you get in trouble with cyclic imports
        from .utils import get_project_translation_from_parent

        language_code = translation.get_language()
        project_translation = get_project_translation_from_parent(parent=self,
                                                                  language_code=language_code,
                                                                  fallback_language='en',
                                                                  fallback_any=True)

        return project_translation.get_absolute_url()




class Question(TranslatableModel):
    """
    A project question
    """
    topic = models.ForeignKey(Topic, related_name="questions")
    weight = models.IntegerField(_("Weight"), default=0)
    translations = TranslatedFields(
        content = models.CharField(_("Content"), max_length=512)
    )
    
    def __unicode__(self):
        return self.safe_translation_getter('content', str(self.pk))
            
class Answer(TranslatableModel):
    question = models.ForeignKey(Question, related_name="answers")
    project = models.ForeignKey(I4pProject, related_name="answers")
    translations = TranslatedFields(
        content = models.TextField(_("Content"))
    )
    class Meta:
        unique_together = (("question", "project"), )
        
    def __unicode__(self):
        return 'Answer to: [%s]' % (self.question,)

    def get_content():
        return self.safe_translation_getter('content')

class I4pProjectTranslation(models.Model):
    """
    A translation of a project
    """

    PROGRESS_CHOICES = [
        ("EDIT", _("In edition")),
        ("FULL", _("Complete")),
    ]
    class Meta:
        unique_together = ('language_code', 'slug')

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
                                max_length=5, choices=PROGRESS_CHOICES, default="EDIT",
                                null=True, blank=True)

    modified = models.DateTimeField(null=True, blank=True)

    baseline = models.CharField(verbose_name=_("one line description"),
                                max_length=180,
                                null=True,
                                blank=True,
                                default=_("One line description")
                                )

    about_section = models.TextField(_("about the project"), null=True, blank=True)
    partners_section = models.TextField(_("who are the partners of this project"), null=True, blank=True)
    callto_section = models.TextField(_("Help request"), null=True, blank=True)
    

    themes = TagField(_("Themes of the project"), null=True, blank=True)

    # @models.permalink
    def get_absolute_url(self):
        return reverse('project_sheet-show', kwargs={'slug': self.slug, 'locale':self.language_code})


    def __unicode__(self):
        return u"Translation of '%d' in '%s' : %s" % (self.project.id, self.language_code, self.slug)


def last_modification_date(sender, instance, **kwargs):
    if sender == Version:
        version = instance
        ct_project = ContentType.objects.get_for_model(I4pProject)
        ct_sheet = ContentType.objects.get_for_model(I4pProjectTranslation)

        if version.content_type == ct_sheet:
            try:
                project_sheet = ct_sheet.model_class().objects.get(id=version.object_id)
                project_sheet.modified = version.revision.date_created
                project_sheet.save()
            except:
                pass
        elif version.content_type == ct_project:
            try:
                project = ct_project.model_class().objects.get(id=version.object_id)
                for project_sheet in project.translations.all():
                    project_sheet.modified = version.revision.date_created
                    project_sheet.save()
            except:
                pass

post_save.connect(last_modification_date, sender=Version)



def get_projectpicture_path(aProjectPicture, filename):
    """
    Generate a random UUID for a picture,
    use the uuid as the track name
    """
    track_uuid = uuid.uuid4()
    name, extension = os.path.splitext(filename)

    dst = 'uploads/projects/%d/pictures/%s%s' % (aProjectPicture.project.id,
                                                 track_uuid,
                                                 extension)
    return dst

class ProjectPicture(ImageModel):
    """
    A picture illustrating a project (jpg, png accepted)
    """
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
    """
    An embeddable Video for a project
    """
    video_url = models.URLField()
    project = models.ForeignKey(I4pProject, related_name="videos")

    def __unicode__(self):
        return u"Video for '%s'" % self.project

class ProjectMember(models.Model):
    """
    A team member of a project
    """
    class Meta:
        unique_together = ('project', 'user')

    project = models.ForeignKey(I4pProject, related_name="detailed_members")
    user = models.ForeignKey(User, related_name="project_memberships")

    role = models.CharField(verbose_name=_("role"),
                            max_length=100,
                            blank=True,
                            null=True)

    comment = models.TextField(verbose_name=_("comment"),
                               blank=True,
                               null=True)

    def __unicode__(self):
        return u"%s - %s" % (self.project, self.user)


# Email on events
@receiver(post_save, sender=I4pProjectTranslation, dispatch_uid='email-on-new-project-translation')
def email_managers_on_new_translation(sender, instance, created, **kwargs):
    if created:
        body = render_to_string('project_sheet/emails/new_translation.txt', {'project_translation': instance})
        mail_managers(subject=_(u'New project/translation added'), message=body)

@receiver(post_save, sender=ProjectMember, dispatch_uid='email-on-member-project-association')
def email_managers_when_a_member_joins_a_project(sender, instance, created, **kwargs):
    if created:
        body = render_to_string('project_sheet/emails/member_joined_project.txt', {'project_member': instance})
        mail_managers(subject=_(u'A member has joined a project'), message=body)


@receiver(post_delete, sender=I4pProjectTranslation, 
          dispatch_uid='delete-parent-project-when-deleting-last-translation')
def delete_parent_if_last_translation(sender, instance, **kwargs):
    """
    When the last translation of a project is deleted, delete the project.
    """
    project = instance.project
    if project.translations.count() == 0:
        project.delete()


# Reversions
VERSIONNED_FIELDS = {
    I4pProject : ['author', 'objectives', 'website', 'project_leader_info', 'location', 'status', 'best_of'],
    I4pProjectTranslation : ['title', 'baseline', 'about_section', 'themes', 'completion_progress']
}

for model, fields in VERSIONNED_FIELDS.iteritems():
    if not reversion.is_registered(model):
        reversion.register(model, fields=fields)

