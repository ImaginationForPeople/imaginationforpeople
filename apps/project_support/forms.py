from apps.forum.forms import SpecificQuestionForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.forum.models import SpecificQuestionType


class ProjectSheetNeedForm(SpecificQuestionForm):
    type = forms.ModelChoiceField(queryset=SpecificQuestionType.objects.filter(type__in=['pj-need', 'pj-help']))