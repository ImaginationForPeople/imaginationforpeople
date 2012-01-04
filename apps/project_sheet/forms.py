#-- encoding: utf-8 --
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Django Forms for a Project Sheet
"""
from django import forms
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory

from ajax_select.fields import AutoCompleteSelectField


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


class I4pProjectObjectivesForm(forms.ModelForm):
    """
    Edit objectives for a given Project
    """
    class Meta:
        model = I4pProject
        fields = ('objectives',)

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


class I4pProjectStatusForm(forms.ModelForm):
    """
    Edit the status of a Project
    """
    class Meta:
        model = I4pProject
        fields = ('status', )



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

    #user = ProjectMemberChoiceField(queryset=User.objects.filter(id__gt= -1).order_by('username'))
    user = AutoCompleteSelectField("members", required=True)

ProjectMemberFormSet = modelformset_factory(ProjectMember, 
                                            extra=0, 
                                            can_delete=True, 
                                            fields=('role', 'comment')
                                            )
