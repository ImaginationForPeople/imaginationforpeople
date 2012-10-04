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
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from tagging.models import TaggedItem

from apps.project_sheet.models import I4pProjectTranslation

from .models import TagCMS

class ProjectsForTagPlugin(CMSPluginBase):
    """
    List of all projects associated to a tag
    """
    name = _("Projects for a tag")
    render_template = "project_sheet/obsolete/projects_for_tag.html"
    model = TagCMS
    
    def render(self, context, instance, placeholder):
        context["tag"] = TaggedItem.objects.get_by_model(I4pProjectTranslation, instance.tag)

        return context

    def __unicode__(self):
        return u"Tag"

plugin_pool.register_plugin(ProjectsForTagPlugin)
