"""
Example on how to use tests for TDD
"""
from django.test import TestCase

from utils import create_parent_project

class TestUtils(TestCase):
    fixtures = ["test_pjsheet"]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_parent_project(self):
        project = create_parent_project()
        self.assertTrue(project.pk  > 0)
        

        











