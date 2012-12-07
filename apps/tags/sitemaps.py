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
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import Tag

from apps.project_sheet.models import I4pProjectTranslation

class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.2

    def items(self):
        project_translations = I4pProjectTranslation.objects.filter(language_code='fr')
        return Tag.objects.usage_for_queryset(project_translations)

    def location(self, tag):
        return reverse('tags:tag-view', kwargs={'tag': tag.name})

