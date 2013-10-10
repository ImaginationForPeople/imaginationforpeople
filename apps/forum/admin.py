from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from apps.tags.models import TaggedCategory
from .models import SpecificQuestion, SpecificQuestionType

from apps.project_sheet.models import I4pProjectTranslation
from apps.workgroup.models import WorkGroup

import autocomplete_light
from askbot.models.question import Thread

autocomplete_light.register(Thread, search_fields=['title'])

class AutocompleteSpecificQuestionContext(autocomplete_light.AutocompleteGenericBase):
    choices = (
        I4pProjectTranslation.objects.all(),
        WorkGroup.objects.all(),
    )
        
    def choice_label(self, choice):
        if isinstance(choice, I4pProjectTranslation) :
            print choice.__dict__
            return u"%s #%s: %s (%s)" % (_('project'),
                                         choice.id,
                                         choice.title,
                                         choice.language_code)
        elif isinstance(choice, WorkGroup):
            return u"%s #%s: %s (%s)" % (_('workgroup'),
                                         choice.id,
                                         choice.name, 
                                         choice.language)
        return autocomplete_light.AutocompleteGenericBase.choice_label(self, choice)
        
    search_fields = (
        ('id', 'title', ),
        ('id', 'name',),
    )

autocomplete_light.register(AutocompleteSpecificQuestionContext)


class SpecificQuestionForm(autocomplete_light.GenericModelForm):
    thread = forms.ModelChoiceField(Thread.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ThreadAutocomplete'))
    context_object = autocomplete_light.GenericModelChoiceField(
        widget=autocomplete_light.ChoiceWidget(
            autocomplete='AutocompleteSpecificQuestionContext',
            autocomplete_js_attributes={'minimum_characters': 0}))

    class Meta:
        model = SpecificQuestion
        exclude = ('content_type', 'object_id')

class SpecificQuestionAdmin(admin.ModelAdmin):
    list_display = ('thread', 'type', 'display_context_object')
    form = SpecificQuestionForm
    
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