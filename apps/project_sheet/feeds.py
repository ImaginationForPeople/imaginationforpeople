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
import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils import translation

from actstream.models import model_stream
from reversion.models import Version

from .models import I4pProject, I4pProjectTranslation
from .utils import get_project_project_translation_recent_changes
from .utils import get_project_translations_from_parents

class LatestChangesFeed(Feed):
    """
    A feed for displaying the latest changes of the project sheets
    """
    title = "Imagination For People latest changes"
    description = "Latest changes in the projects"
    
    def items(self):
        return model_stream(I4pProject)

    def item_title(self, item):
        return item.target.title

    def item_description(self, item):
        return str(item)

    def item_pubdate(self, item):
        return item.timestamp

    def item_link(self, item):
        return item.target.get_absolute_url()

    def link(self):
        return reverse('project_sheet-recent-changes')


class NewProjectsFeed(Feed):
    """
    A feed displaying the newest projects
    """
    title = 'New projects on Imagination For People'
    description = 'Most recent projects added to the website'

    def items(self):
        language_code = translation.get_language()
        return get_project_translations_from_parents(parents_qs=I4pProject.objects.all().order_by('-created')[:20],
                                                     language_code=language_code,
                                                     fallback_language='en',
                                                     fallback_any=True)

    def link(self):
        return reverse('project_sheet-list')

    def item_link(self, item):
        translation.activate(item.language_code)
        return reverse('project_sheet-show', kwargs={'slug': item.slug})

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.baseline

    def item_pubdate(self, item):
        return item.master.created

