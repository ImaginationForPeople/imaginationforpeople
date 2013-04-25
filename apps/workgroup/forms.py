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
Django Forms for Groups
"""
from django import forms
from django.forms.widgets import HiddenInput

from apps.forum.forms import SpecificQuestionForm
from apps.forum.models import SpecificQuestionType
from .models import WorkGroup

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = WorkGroup
        fields = ('name', 'description', 'language', 'tags', 'picture', 'outside_url')

class GroupEditForm(forms.ModelForm):
    class Meta:
        model = WorkGroup
        fields = ('name', 'description', 'language', 'tags', 'picture', 'outside_url')

class WorkgroupDiscussionForm(SpecificQuestionForm):
    """
    Form to create a workgroup discussion
    """
    type = forms.ModelChoiceField(widget=HiddenInput(), 
                                  queryset=SpecificQuestionType.objects.filter(type="wg-discuss"),
                                  initial=SpecificQuestionType.objects.get(type="wg-discuss"))
