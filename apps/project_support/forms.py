from django import forms
from askbot.forms import TitleField, QuestionEditorField
from apps.project_sheet.models import I4pProjectTranslation
from apps.tags.models import TaggedCategory
from django.forms import widgets
from .models import SUPPORT_TYPE_CHOICES

class ProjectSupportProposalForm(forms.Form):
    project_translation = forms.ModelChoiceField(queryset=I4pProjectTranslation.objects.all(),
                                     widget=widgets.HiddenInput)
    type = forms.TypedChoiceField(choices=SUPPORT_TYPE_CHOICES,
                                  widget=forms.RadioSelect)
    category = forms.ModelChoiceField(queryset=TaggedCategory.objects.all())

    title = TitleField()
    text = QuestionEditorField()