from django import forms

from apps.forum.models import SpecificQuestionType
from apps.forum.forms import SpecificQuestionForm

class ProjectSheetNeedForm(SpecificQuestionForm):
    """
    Form to create a project sheet support
    """
    type = forms.ModelChoiceField(queryset=SpecificQuestionType.objects.filter(type__in=['pj-need', 'pj-help']))