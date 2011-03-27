from django import forms
from django.utils.translation import ugettext as _

from tagging.forms import TagField

from .models import I4pProject, I4pProjectTranslation, ProjectReference
from django.forms.models import modelform_factory, modelformset_factory

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

ProjectReferenceForm = modelform_factory(ProjectReference)
ProjectReferenceFormSet = modelformset_factory(ProjectReference, extra=0, can_delete=True)





