"""
Django Admin for a Project Sheet
"""
from django.contrib import admin

from oembed_works.models import StoredOEmbedResponse
from reversion.admin import VersionAdmin

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


admin.site.register(I4pProject, I4pProjectAdmin)
admin.site.register(I4pProjectTranslation, VersionAdmin)

admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)

admin.site.register(ProjectMember, admin.ModelAdmin)

admin.site.register(StoredOEmbedResponse, admin.ModelAdmin)
