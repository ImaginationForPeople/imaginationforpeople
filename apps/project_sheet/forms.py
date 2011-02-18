from django import forms
from django.utils.translation import ugettext as _

from tagging.forms import TagField

from .models import I4pProject

class I4pProjectRelatedForm(forms.ModelForm):
    """
    Edit themes for a given Project
    """
    class Meta:
        model = I4pProject
        fields = ('themes', 'objective')

    themes = TagField(label=_("themes"),
                      widget=forms.Textarea,
                      help_text=_("Enter your themes, using a comma-separated list.")
                      )





