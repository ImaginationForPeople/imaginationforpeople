"""
Django Admin for a Project Sheet
"""
from django.contrib import admin

from oembed_works.models import StoredOEmbedResponse
from reversion.admin import VersionAdmin

from .models import I4pProject, I4pProjectTranslation
from .models import ProjectVideo, ProjectPicture, ProjectMember

admin.site.register(I4pProject, VersionAdmin)
admin.site.register(I4pProjectTranslation, VersionAdmin)

admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)

admin.site.register(ProjectMember, admin.ModelAdmin)

admin.site.register(StoredOEmbedResponse, admin.ModelAdmin)
