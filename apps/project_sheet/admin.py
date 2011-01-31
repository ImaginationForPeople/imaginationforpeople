# import stuff we need from django
from django.contrib import admin
from django.conf import settings

# import app specific shit
from .models import GenericPage, GenericPageTranslation

# create the inline to handle translation
class GenericPageTranslationInline(admin.StackedInline):
    model = GenericPageTranslation
    extra = 1
    max_num = len(settings.LANGUAGES)-1
    fieldsets = (
        (None, {
            'fields': ['language',]
        }),
        ('Translation', {
            'fields': ['title','content'],
            'classes': ['collapse',],
        }),
    )

# create the admin model
class GenericPageAdmin(admin.ModelAdmin):
    fields = ['title', 'content',]
    inlines = (GenericPageTranslationInline,)

# register with CMS
admin.site.register(GenericPage, GenericPageAdmin)
