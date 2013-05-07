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
from askbot.models.question import Thread
"""
Django Admin for a Project Sheet
"""
from django.contrib import admin

import hvad.admin
from oembed_works.models import StoredOEmbedResponse
from reversion.admin import VersionAdmin

from apps.partner.models import Partner

from .models import I4pProject, I4pProjectTranslation, Objective
from .models import ProjectVideo, ProjectPicture, ProjectMember
from .models import Topic, Question, Answer, SiteTopic

class PartnerInline(admin.TabularInline):
    model = Partner.projects.through
    extra = 1

class TranslationInline(admin.StackedInline):
    model = I4pProjectTranslation

class I4pProjectAdmin(VersionAdmin):
    inlines = (
        PartnerInline,
        TranslationInline,
        )
    list_display = ('__unicode__', 'status', 'best_of', 'created')
    date_hierarchy = 'created'
    list_filter = ['site', 'status', 'best_of', 'topics']
    
class QuestionAdmin(hvad.admin.TranslatableAdmin):
    list_display = ('topic', 'weight', 'all_translations')

class TopicAdmin(hvad.admin.TranslatableAdmin):
    list_display = ('__str__', 'all_translations')

class SiteTopicAdmin(VersionAdmin):
    list_display = ('topic', 'order', 'site')

class AnswerAdmin(hvad.admin.TranslatableAdmin):
    list_display = ('__str__', 'all_translations')

class ObjectiveAdmin(hvad.admin.TranslatableAdmin):
    list_display = ('__str__', 'all_translations')

    
admin.site.register(I4pProject, I4pProjectAdmin)

admin.site.register(Topic, TopicAdmin)

admin.site.register(Question, QuestionAdmin)

admin.site.register(Answer, AnswerAdmin)

admin.site.register(SiteTopic, SiteTopicAdmin)

admin.site.register(Objective, ObjectiveAdmin)

admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)

admin.site.register(ProjectMember, admin.ModelAdmin)

admin.site.register(StoredOEmbedResponse, admin.ModelAdmin)
