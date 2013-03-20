from django.contrib import admin
from .models import SpecificQuestion, SpecificQuestionType
from apps.tags.models import TaggedCategory
from django.contrib.contenttypes.models import ContentType


class SpecificQuestionAdmin(admin.ModelAdmin):
    list_display = ('thread', 'type', 'context_object')
    
    def context_object(self, obj):
        return "%s : %s " % (ContentType.objects.get_for_model(obj.context_object), obj.context_object)
    context_object.short_description = 'Context object'

class SpecificQuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'label', 'allowed_category_tree')
    list_editable = ('key', 'label', 'allowed_category_tree')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "allowed_category_tree":
            kwargs["queryset"] = TaggedCategory.objects.filter(parent__isnull=True)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(SpecificQuestion, SpecificQuestionAdmin)
admin.site.register(SpecificQuestionType, SpecificQuestionTypeAdmin)