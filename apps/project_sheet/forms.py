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
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from ajax_select.fields import AutoCompleteSelectField
from nani.forms import TranslatableModelForm

from apps.i4p_base.models import Location

from .models import I4pProject, I4pProjectTranslation, ProjectPicture, ProjectVideo
from .models import ProjectReference, ProjectMember, Answer

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
        fields = ('website', 'status')


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

class ProjectMemberAddForm(forms.ModelForm):
    """
    Let a user adds her/hisself to the project
    """
    class Meta:
        model = ProjectMember
        fields = ('role', 'comment')

    role = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Specify your role in the project")}))
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _("Explain briefly your motivation about the project...")}))

ProjectMemberFormSet = modelformset_factory(ProjectMember, 
                                            extra=0, 
                                            can_delete=True, 
                                            fields=('role', 'comment')
                                            )

class AnswerForm(TranslatableModelForm):
    class Meta:
        model = Answer
        fields = ('content',)


class ProjectPictureAddForm(forms.ModelForm):
    class Meta:
        model = ProjectPicture
        fields = ('original_image', 'desc', 'license', 'author', 'source')

class ProjectVideoAddForm(forms.ModelForm):
    class Meta:
        model = ProjectVideo
        fields = ('video_url', )