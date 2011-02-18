from django.contrib import admin
from django.conf import settings

from .models import I4pProject, I4pProjectTranslation
from .models import ProjectVideo, ProjectPicture

# create the inline to handle translation
class I4pProjectTranslationInline(admin.StackedInline):
    model = I4pProjectTranslation
    extra = 1
    max_num = len(settings.LANGUAGES)-1
    fieldsets = (
        (None, {
            'fields': ['language',]
        }),
        ('Translation', {
            'fields': ['title', 'baseline', 'about_section', 'uniqueness_section', 'value_section', 'scalability_section'],
            'classes': ['collapse',],
        }),
    )

# create the admin model
class I4pProjectAdmin(admin.ModelAdmin):
    fields = ['title', 'baseline', 'about_section', 'uniqueness_section', 'value_section', 'scalability_section']
    inlines = (I4pProjectTranslationInline,)

# register with CMS
admin.site.register(I4pProject, I4pProjectAdmin)



admin.site.register(ProjectVideo, admin.ModelAdmin)
admin.site.register(ProjectPicture, admin.ModelAdmin)