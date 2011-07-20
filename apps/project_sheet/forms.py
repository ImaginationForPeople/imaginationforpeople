"""
Django Forms for a Project Sheet
"""
from django import forms
from django.forms.models import modelformset_factory

from django.contrib.auth.models import User

from apps.i4p_base.models import Location

from .models import I4pProject, I4pProjectTranslation, ProjectReference, ProjectMember

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

ProjectReferenceFormSet = modelformset_factory(ProjectReference, extra=1, can_delete=True)

class I4pProjectInfoForm(forms.ModelForm):
    """
    Edit the extra infos of a Project
    """
    class Meta:
        model = I4pProject
        fields = ('website',)


class I4pProjectLocationForm(forms.ModelForm):
    """
    Edit the location info of a Project
    """
    class Meta:
        model = Location
        fields = ('address', 'country',)

class ProjectMemberChoiceField(forms.ModelChoiceField):
    """
    Show firstname and lastname instead of username if possible
    """
    def label_from_instance(self, aUser):
        res = u""
        if aUser.first_name and aUser.last_name:
            res = u"%s %s (%s)" % (aUser.first_name,
                                   aUser.last_name,
                                   aUser.username)
        else:
            res = u"%s" % aUser.username

        return res

class ProjectMemberForm(forms.ModelForm):
    """
    A member for a project
    """
    class Meta:
        model = ProjectMember
        fields = ('user', 'role', 'comment')

    user = ProjectMemberChoiceField(queryset=User.objects.filter(id__gt= -1).order_by('username'))

ProjectMemberFormSet = modelformset_factory(ProjectMember, extra=0, can_delete=True, fields=('role', 'comment'))
