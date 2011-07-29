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
        











