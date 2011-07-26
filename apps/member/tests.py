"""
Example on how to use tests for TDD
"""
from django.test import TestCase

class TestExample(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_something(self):
        """
        That must start with test_
        """
        print "this is a test"

        





