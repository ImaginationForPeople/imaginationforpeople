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
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from userena.contrib.umessages.forms import ComposeForm
from userena.forms import SignupForm, EditProfileForm

from .models import I4pProfile
from .fields import UserMessageRecipientField
from .utils import fix_username

class I4PSignupForm(SignupForm):
    """
    Form to signup with first and last names
    """
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))

    def __init__(self, *args, **kwargs):
        super(I4PSignupForm, self).__init__(*args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder = ['first_name',
                                 'last_name',
                                 'email',
                                 'password1',
                                 'password2']


    def save(self):
        firstname = self.cleaned_data['first_name'].title()
        lastname = self.cleaned_data['last_name'].title()
        fullname = "%s%s" % (firstname, lastname)
        username = fix_username(fullname)

        users = User.objects.filter(username__istartswith=username)
        if users.count() > 0:
            username = "%s%s" % (username, users.count())

        self.cleaned_data['username'] = username

        new_user = super(I4PSignupForm, self).save()
        new_user.first_name = firstname
        new_user.last_name = lastname

        new_user.save()
        return new_user


class I4PEditProfileForm(EditProfileForm):
    gender = forms.ChoiceField(choices=I4pProfile.GENDER_TYPE,
                               widget=forms.RadioSelect,
                               required=False,
                               label=_("gender"))
    class Meta:
        model = I4pProfile
        exclude = ('registration_site',
                   'user',
                   
                   'status',
                   'reputation',
                   'gold',
                   'silver',
                   'bronze',
                   'questions_per_page',
                   'last_seen',
                   'interesting_tags',
                   'ignored_tags',
                   'subscribed_tags',
                   'show_marked_tags',
                   'email_tag_filter_strategy',
                   'email_signature',
                   'display_tag_filter_strategy',
                   'new_response_count',
                   'seen_response_count',
                   'consecutive_days_visit_count',
                   'is_fake',)


class AutoCompleteComposeForm(ComposeForm):
    """
    Subclass umessages form to add recipient autocompletion.
    """
    to = UserMessageRecipientField("members", required=True)
