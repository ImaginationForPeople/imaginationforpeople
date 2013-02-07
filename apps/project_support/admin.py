from django.contrib import admin
from .models import ProjectSupport


class ProjectSupportAdmin(admin.ModelAdmin):
    list_display = ('type', 'category', 'thread')
    list_filter = ('type',)
    pass

admin.site.register(ProjectSupport, ProjectSupportAdmin)