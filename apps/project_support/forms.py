from django import forms
from askbot.forms import TitleField, QuestionEditorField
from apps.project_sheet.models import I4pProjectTranslation
from apps.tags.models import TaggedCategory
from django.forms import widgets
from .models import SUPPORT_TYPE_CHOICES, ProjectSupport

class ProjectSupportProposalForm(forms.ModelForm):
    title = TitleField()
    text = QuestionEditorField()
    
    class Meta:
        model = ProjectSupport
        exclude=('project_translation', 'thread',)