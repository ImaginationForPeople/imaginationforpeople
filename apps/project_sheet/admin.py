from django.contrib import admin
from django.conf import settings

from .models import I4pProject, I4pProjectTranslation
from .models import ProjectVideo, ProjectPicture

from reversion.admin import VersionAdmin
from oembed_works.models import StoredOEmbedResponse

admin.site.register(I4pProject, VersionAdmin)
admin.site.register(I4pProjectTranslation, VersionAdmin)

admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)

admin.site.register(StoredOEmbedResponse, admin.ModelAdmin)
