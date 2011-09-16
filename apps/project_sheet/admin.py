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
"""
Django Admin for a Project Sheet
"""
from django.contrib import admin
from nani import admin as nani_admin

from oembed_works.models import StoredOEmbedResponse
from reversion.admin import VersionAdmin

from .models import I4pProject, I4pProjectTranslation, Objective
from .models import ProjectVideo, ProjectPicture, ProjectMember
from apps.partner.models import Partner

from .models import I4pProject, I4pProjectTranslation
from .models import ProjectVideo, ProjectPicture, ProjectMember

class PartnerInline(admin.TabularInline):
    model = Partner.projects.through
    extra = 1

class I4pProjectAdmin(VersionAdmin):
    inlines = (
        PartnerInline,
        )

class ObjectiveAdmin(nani_admin.TranslatableAdmin):
    list_display = ('__str__', 'all_translations')

admin.site.register(I4pProject, I4pProjectAdmin)

admin.site.register(Objective, ObjectiveAdmin)

admin.site.register(I4pProjectTranslation, VersionAdmin)

admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)

admin.site.register(ProjectMember, admin.ModelAdmin)

admin.site.register(StoredOEmbedResponse, admin.ModelAdmin)
