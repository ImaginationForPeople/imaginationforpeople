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
import re

from apps.i4p_base.utils import remove_accents

def fix_username(original_name):
    """
    Modify a username to comply with the site username policy, basically getting
    rid of accents, spaces and special characters and making sure there's no
    duplicate, even with a different case.
    """
    from django.contrib.auth.models import User

    username = re.sub("[^a-zA-Z0-9]", "", remove_accents(original_name))
    name, idx = username, 2
    while True:
        try:
            User.objects.get(username__iexact=name)
            name = username + str(idx)
            idx += 1
        except User.DoesNotExist:
            username = name
            break
    return username
