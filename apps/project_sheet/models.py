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
from askbot.models.question import Thread
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
from django.core.urlresolvers import reverse
from django.core.mail import mail_managers
from django.db import models
from django.db.models.signals import post_save, post_delete, class_prepared
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import translation


from autoslug.fields import AutoSlugField
from cms.models.pluginmodel import CMSPlugin
from imagekit.models import ImageModel
from licenses.fields import LicenseField
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager
import reversion
import reversion.models

from south.modelsinspector import add_introspection_rules
from south.modelsinspector import add_ignored_fields
from tagging.fields import TagField
from tagging.models import Tag

from apps.member.models import I4pProfile
from apps.i4p_base.models import Location
from apps.i4p_base.managers import CurrentSiteTranslationManager

# Add Introspector for south: django-licenses field
add_introspection_rules([], ["^licenses\.fields\.LicenseField"])

VERSIONED_FIELDS = {
    'I4pProject' : ['author', 'objectives', 'website', 'project_leader_info', 'location', 'status', 'best_of'],
    'I4pProjectTranslation': ['title', 'baseline', 'language_code', 'about_section', 'themes', 'completion_progress', 'master'],
    'AnswerTranslation': ['content', 'master']
}
    
# Keep this before classes, otherwise I4pProject won't be caught
@receiver(signal=class_prepared)
def register_versioned_models(sender, **kwargs):
    if sender.__name__ in VERSIONED_FIELDS:
        fields = VERSIONED_FIELDS[sender.__name__]
        if not reversion.is_registered(sender):
            reversion.register(sender, fields=fields)


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

class I4pProject(TranslatableModel):
    """
    Root object for a project. Holds only shared data
    """

    STATUS_CHOICES = [
        ('IDEA', _('Concept')),
        ('BEGIN', _('Starting')),
        ('WIP', _('In development')),
        ('END', _('Mature')),
    ]
    
    PROGRESS_CHOICES = [
        ("EDIT", _("In edition")),
        ("FULL", _("Complete")),
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

    topics = models.ManyToManyField(SiteTopic, verbose_name=_('topics'),
                                    related_name='projects')
    
    # dynamicsites
    site = models.ManyToManyField(Site, help_text=_('The sites on which this project sheet is accessible.'), 
                                  verbose_name=_("sites"),
                                  related_name='projects')
    objects = TranslationManager()
    on_site = CurrentSiteTranslationManager()
    
    add_ignored_fields(["^dynamicsites\.fields\.FolderNameField"])
    add_ignored_fields(["^dynamicsites\.fields\.SubdomainListField"])
    
    translations = TranslatedFields(
        meta = {'unique_together' : [('language_code', 'slug')]},
        
        language_code = models.CharField(_('language'),
                                         max_length=6,
                                         choices=settings.LANGUAGES),
        
        title = models.CharField(_("title"), max_length=80,
                                 default=_("My Project Title")),
        
        slug = AutoSlugField(populate_from="title",
                             always_update=True,
                             unique_with=['language_code']),
        
        completion_progress = models.CharField(verbose_name=_('status'),
                                               max_length=5, choices=PROGRESS_CHOICES, default="EDIT",
                                               null=True, blank=True),
        
        modified = models.DateTimeField(null=True, blank=True),
        
        baseline = models.CharField(verbose_name=_("one line description"),
                                    max_length=180,
                                    null=True,
                                    blank=True,
                                    default=_("One line description")
                                ),
        
        about_section = models.TextField(_("about the project"), null=True, blank=True),
        partners_section = models.TextField(_("who are the partners of this project"), null=True, blank=True),
        callto_section = models.TextField(_("Help request"), null=True, blank=True),
        
        themes = TagField(_("Themes of the project"), null=True, blank=True),
        
    )

    def get_primary_picture(self):
        """
        Return the first picture, if available
        """
        if len(self.pictures.all()):
            return self.pictures.all()[0]
        else:
            return None
    
    def __unicode__(self):
        return self.lazy_translation_getter('title', 'Project: %s' % self.pk)

    def get_absolute_url(self):
        current_language = translation.get_language()

        # Don't move this into the 'activate' block or hvad will get
        # crazy with the language change
        slug = self.lazy_translation_getter('slug') 

        translation.activate(self.language_code)
        url = reverse('project_sheet-show', kwargs={'slug': slug})
        translation.activate(current_language)
        
        return url

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
        return u'Answer to: [%s] (Project %s)' % (self.question, self.project)


# XXX HVAD
# def last_modification_date(sender, instance, **kwargs):
#     if sender == Version:
#         version = instance
#         ct_project = ContentType.objects.get_for_model(I4pProject)
#         ct_sheet = ContentType.objects.get_for_model(I4pProjectTranslation)

#         if version.content_type == ct_sheet:
#             try:
#                 project_sheet = ct_sheet.model_class().objects.get(id=version.object_id)
#                 project_sheet.modified = version.revision.date_created
#                 project_sheet.save()
#             except:
#                 pass
#         elif version.content_type == ct_project:
#             try:
#                 project = ct_project.model_class().objects.get(id=version.object_id)
#                 for project_sheet in project.translations.all():
#                     project_sheet.modified = version.revision.date_created
#                     project_sheet.save()
#             except:
#                 pass

# post_save.connect(last_modification_date, sender=Version)



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


# XXX: HVAD
# Email on events
# @receiver(post_save, sender=I4pProjectTranslation, dispatch_uid='email-on-new-project-translation')
# def email_managers_on_new_translation(sender, instance, created, **kwargs):
#     if created:
#         body = render_to_string('project_sheet/emails/new_translation.txt', {'project_translation': instance})
#         mail_managers(subject=_(u'New project/translation added'), message=body)

# @receiver(post_save, sender=ProjectMember, dispatch_uid='email-on-member-project-association')
# def email_managers_when_a_member_joins_a_project(sender, instance, created, **kwargs):
#     if created:
#         body = render_to_string('project_sheet/emails/member_joined_project.txt', {'project_member': instance})
#         mail_managers(subject=_(u'A member has joined a project'), message=body)


# @receiver(post_delete, sender=I4pProjectTranslation, 
#           dispatch_uid='delete-parent-project-when-deleting-last-translation')
# def delete_parent_if_last_translation(sender, instance, **kwargs):
#     """
#     When the last translation of a project is deleted, delete the project.
#     """
#     try:
#         project = instance.master
#     except I4pProject.DoesNotExist:
#         # Can happen if the parent when already deleted
#         return
        
#     if project.translations.count() == 0:
#         project.delete()

class TagCMS(CMSPlugin):
    tag = models.ForeignKey(Tag) #models.CharField(_('Tag'), choices=gen_tag_list(), max_length=50) 
        
    def copy_relations(self, oldinstance):
        self.tag = oldinstance.tag

from actstream.models import actstream_register_model
actstream_register_model(I4pProject)
actstream_register_model(I4pProject.objects.translations_model)
actstream_register_model(User)
actstream_register_model(Answer)
