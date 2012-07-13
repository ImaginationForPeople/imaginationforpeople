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

from .models import WorkGroupCMS, WorkGroup, TagCMS
from .utils import get_ml_members

from apps.project_sheet.models import I4pProject

class BaseWorkGroupPlugin(CMSPluginBase):
    """
    Workgroup base for the CMS
    """
    model = WorkGroupCMS
   
    def render(self, context, instance, placeholder):
        workgroup = instance.workgroup
        members = get_ml_members(workgroup)

        context['ml_member_list'] = []
        context['ml_nonmember_list'] = []        
        for member in members:
            try:
                found_member = User.objects.get(email=member[0])
                context['ml_member_list'].append(found_member)
            except User.DoesNotExist:
                context['ml_nonmember_list'].append(User(email=member[0]))


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

from apps.project_sheet.utils import get_project_translation_from_parent

class ProjectsForTagPlugin(CMSPluginBase):
    """
    List of all projects associated to a tag
    """
    name = _("Projects for a tag")
    render_template = "workgroup/projects_for_tag.html"
    model = TagCMS
    
    def render(self, context, instance, placeholder):
        language_code = translation.get_language()
        projects = I4pProject.objects.filter(objectives=instance.tag.id)
        i18n_projects = []
        
        for project in projects:
            i18n_project = get_project_translation_from_parent(project, language_code, fallback_language="en", fallback_any="True")
            i18n_projects.append(i18n_project)
            
        context["tag"] = i18n_projects

        return context

    def __unicode__(self):
        return u"Tag"

plugin_pool.register_plugin(ProjectsForTagPlugin)
