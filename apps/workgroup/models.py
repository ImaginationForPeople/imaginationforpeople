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
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug.fields import AutoSlugField

from django_mailman.models import List

class WorkGroup(models.Model):
    """
    A workgroup in a given language, for a given thematic.
    """
    slug = AutoSlugField(populate_from='name',
                         always_update=True)

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


    def __unicode__(self):
        return u"%s (%s)" % (self.name,
                             self.get_language_display())


    @models.permalink
    def get_absolute_url(self):
        return ('workgroup-detail', (self.slug,))

    

from cms.models.pluginmodel import CMSPlugin
from utils import gen_tag_list

class WorkGroupCMS(CMSPlugin):
    workgroup = models.ForeignKey(WorkGroup)

    def copy_relations(self, oldinstance):
        self.workgroup = oldinstance.workgroup

class TagCMS(CMSPlugin):
    tag = models.CharField(_('Tag'), choices=gen_tag_list(), max_length=50) 
        
    def copy_relations(self, oldinstance):
        self.tag = oldinstance.tag