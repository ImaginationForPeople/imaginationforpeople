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
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from .models import WorkGroupCMS, WorkGroup
from .utils import get_ml_members

class BaseWorkGroupPlugin(CMSPluginBase):
    """
    Workgroup base for the CMS
    """
    model = WorkGroupCMS
   
    def render(self, context, instance, placeholder):
        workgroup = instance.workgroup
        context['workgroup'] = workgroup

        return context

    def __unicode__(self):
        return u"Workgroup %s" % self.workgroup.slug

class WorkGroupPlugin(BaseWorkGroupPlugin):
    """
    Workgroup (Un)subscribe button for the CMS
    """
    name = _("WorkGroup (un)subscribe button")
    render_template = "workgroup/cms_subscribe_button.html"
    
    def __unicode__(self):
        return u"Workgroup Button %s" % self.workgroup.slug
    
plugin_pool.register_plugin(WorkGroupPlugin)


class SubscribersWorkGroupPlugin(BaseWorkGroupPlugin):
    """
    Workgroup subscribers list for the CMS
    """
    name = _("WorkGroup subscribers list")
    render_template = "workgroup/cms_workgroup_subscribers.html"

    def __unicode__(self):
        return u"Workgroup Subscribers %s" % self.workgroup.slug

plugin_pool.register_plugin(SubscribersWorkGroupPlugin)
