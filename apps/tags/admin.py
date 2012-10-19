from django.contrib import admin

from categories.admin import CategoryBaseAdmin

from .models import TaggedCategory

class TaggedCategoryAdmin(CategoryBaseAdmin):
    exclude = ['tag']

admin.site.register(TaggedCategory, TaggedCategoryAdmin)
