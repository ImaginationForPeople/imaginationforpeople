from django.contrib import admin
from django.conf import settings

from .models import I4pProject, I4pProjectTranslation
from .models import ProjectVideo, ProjectPicture

admin.site.register(I4pProject)
admin.site.register(I4pProjectTranslation)

admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)
