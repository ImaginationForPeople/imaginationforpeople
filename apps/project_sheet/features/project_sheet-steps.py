from django.core.urlresolvers import reverse
from django.test.client import Client

from lettuce import before, step, world
from lettuce.django import django_url

from nose.tools import assert_equals

from lettuce import *
from radish.features import base
from radish.settings import *

from apps.project_sheet.models import I4pProject

@step(r'I want to change the themes of my project')
def project_sheet_change_theme(step):
    response = world.browser.get(world.edit_theme_url)
    assert(response.status_code == '200')

@step(r'I tag it with "(.*)"')
def project_sheet_tag_it(step, someTags):
    world.browser.post(world.edit_theme_url,
                       {'themes': someTags}
                       )

@step(r'My project is at least tagged with "(.*)"')
def project_sheet_is_tagged(step, someTags):
    project = I4pProject.objects.get(slug=world.project_slug)

    for tag in parse_tag_input(someTags):
        assert(tag in project.themes)







