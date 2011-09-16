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
TDD for i4p_base
"""
from django.test import TestCase

from .models import Location

from .templatetags.i4p_tags import url_target_blank

class TestI4pBaseTags(TestCase):
    def test_url_target_blank(self):
        res = url_target_blank("<a href='plop.html'>coin</a>")
        self.assertEqual(res, """<a target="_blank" href='plop.html'>coin</a>""")
        











