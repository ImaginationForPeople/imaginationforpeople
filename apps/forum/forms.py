from django import forms
from askbot.forms import TitleField, QuestionEditorField
from .models import SpecificQuestion
from django.forms.widgets import HiddenInput
from django.contrib.contenttypes.models import ContentType

class SpecificQuestionForm(forms.ModelForm):
    title = TitleField()
    text = QuestionEditorField()
    
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(),
                                          widget=HiddenInput())
    object_id = forms.IntegerField(widget=HiddenInput())
    
    class Meta:
        model = SpecificQuestion
        exclude=('thread',)