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

from django.forms import ValidationError
from django.utils.translation import ugettext as _

from ajax_select import get_lookup
from ajax_select.fields import AutoCompleteSelectMultipleField


class UserMessageRecipientField(AutoCompleteSelectMultipleField):
    """
    Subclassing ajax_select.fields.AutoCompleteSelectMultipleField because its
    clean method returns a list of ids but userena.contrib.umessages requires a
    list of user objects.
    """
    def clean(self, value):
        """
        Subclassed clean method which returns a list of user objects.
        """
        if value:
            lookup = get_lookup(self.channel)
            objs = lookup.get_objects(value)
            if not objs:
                # Someone else might have deleted them while writing the
                # message
                if len(value) > 1:
                    error_message = _("Recipients not found")
                else:
                    error_message = _("Recipient not found")
                raise ValidationError(error_message)
            return objs
        elif self.required:
            raise ValidationError(self.error_messages['required'])
        return None
