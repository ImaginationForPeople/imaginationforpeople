from django import forms
from django.utils.translation import ugettext as _

from tagging.forms import TagField

from .models import I4pProject, I4pProjectTranslation

class I4pProjectThemesForm(forms.ModelForm):
    """
    Edit themes for a given Project
    """
    class Meta:
        model = I4pProjectTranslation
        fields = ('themes',)

    #themes = TagField(label=_("themes"),
    #                  widget=forms.Textarea,
    #                  help_text=_("Enter your themes, using a comma-separated list.")
    #                  )


class I4pProjectObjectiveForm(forms.ModelForm):
    """
    Edit objective for a given Project
    """
    class Meta:
        model = I4pProject
        fields = ('objective',)






