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
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as geomodels

from askbot.models.question import Thread
from autoslug.fields import AutoSlugField
from cms.models.pluginmodel import CMSPlugin
from django_mailman.models import List
from tagging.fields import TagField


from apps.project_sheet.models import I4pProject


def get_grouppicture_path(aWorkGroup, filename):
    """
    Generate a random UUID for a picture,
    use the uuid as the track name
    """
    name, extension = os.path.splitext(filename)

    dst = 'uploads/groups/%s/pictures/cover.%s' % (aWorkGroup.slug,
                                                   extension)
    return dst


class WorkGroup(models.Model):
    """
    A workgroup in a given language, for a given thematic.
    """
    slug = AutoSlugField(populate_from='name',
                         always_update=False)

    name = models.CharField(verbose_name=_('name'),
                            max_length=150)

    language = models.CharField(verbose_name=_('spoken language'),
                                max_length=2,
                                choices=settings.LANGUAGES)

    description = models.TextField(verbose_name=_('Description'),
                                   null=True,
                                   blank=True)
    
    mailing_list = models.ForeignKey(List, 
                                     default=None, 
                                     null=True, blank=True)

    visible = models.BooleanField(verbose_name=_('visible'), 
                                  default=True)

    geom = geomodels.PolygonField(verbose_name=_('Group geographic area'),
                                null=True,
                                blank=True,
                                help_text=_(u"If your group is geographic in nature, specify it's outling here.   The platform will display a map of projects, and try to fit this outline in the visible area")
                                )

    projects = models.ManyToManyField(I4pProject,
                                      verbose_name=_('Linked Projects'),
                                      related_name='workgroups',
                                      blank=True)

    tags = TagField(_("Tags of the group"), null=True, blank=True)

    picture = models.ImageField(upload_to=get_grouppicture_path, null=True, blank=True)

    outside_url = models.URLField(_('External URL'),
                                  null=True,
                                  blank=True,
                                  help_text=_("A URL that points to the real discussion tool, if we're not using the built-in (eg Facebook group URL).")
                              )
    
    iframe_home_src = models.URLField(_('iframe for home page source URL'),
                                 null=True,
                                 blank=True,
                                 help_text=_("A URL that points to the collaborative tool used by the group. If not null, will replace the built-in wiki")
                              )
                              
    iframe_description_src = models.URLField(_('iframe for description page source URL'),
                                 null=True,
                                 blank=True,
                                 help_text=_("A URL that points to the collaborative tool used by the group. If not null, will replace the built-in wiki")
                               )

    subscribers = models.ManyToManyField(User,
                                         verbose_name=_("Subscribers"),
                                         related_name='workgroups',
                                         blank=True
                                      )
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name,
                             self.get_language_display())


    @models.permalink
    def get_absolute_url(self):
        return ('workgroup-detail', (self.slug,))


class WorkGroupCMS(CMSPlugin):
    workgroup = models.ForeignKey(WorkGroup)

    def copy_relations(self, oldinstance):
        self.workgroup = oldinstance.workgroup
