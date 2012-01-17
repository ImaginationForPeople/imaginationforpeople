# -*- coding: UTF-8 -*-
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

from ajax_select import get_lookup
from ajax_select.fields import AutoCompleteSelectField
from django import forms

class UserMessageRecipientField(AutoCompleteSelectField):
    """
    Subclassing ajax_select.fields.AutoCompleteSelectField because its clean
    method returns a single object but userena.contrib.umessages needs a list of
    user objects. In this version, our clean method returns a list. 
    """
    def clean(self, value):
        if value:
            lookup = get_lookup(self.channel)
            objs = lookup.get_objects( [ value] )
            if len(objs) != 1:
                # someone else might have deleted it while you were editing
                # or your channel is faulty
                # out of the scope of this field to do anything more than tell you it doesn't exist
                raise forms.ValidationError(u"%s cannot find object: %s" % (lookup,value))
            return objs
        else:
            if self.required:
                raise forms.ValidationError(self.error_messages['required'])
            return None

