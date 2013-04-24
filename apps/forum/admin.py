from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from apps.tags.models import TaggedCategory
from .models import SpecificQuestion, SpecificQuestionType

class SpecificQuestionAdmin(admin.ModelAdmin):
    list_display = ('thread', 'type', 'display_context_object')
    #form = SpecificQuestionForm
    
    def display_context_object(self, obj):
        return u"%s : %s" % (ContentType.objects.get_for_model(obj.context_object), obj.context_object)
    display_context_object.short_description = u"Context object"

class SpecificQuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'allowed_category_tree')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "allowed_category_tree":
            kwargs["queryset"] = TaggedCategory.objects.filter(parent__isnull=True)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(SpecificQuestion, SpecificQuestionAdmin)
admin.site.register(SpecificQuestionType, SpecificQuestionTypeAdmin)