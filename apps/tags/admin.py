from django.contrib import admin

from categories.admin import CategoryBaseAdmin

from .models import TaggedCategory

admin.site.register(TaggedCategory, CategoryBaseAdmin)
