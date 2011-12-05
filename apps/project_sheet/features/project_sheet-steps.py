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

from django.core.urlresolvers import reverse
from django.test.client import Client
from lettuce import before, step, world
from lettuce.django import django_url
from tagging.utils import parse_tag_input

from apps.project_sheet.utils import create_project_translation
from apps.project_sheet.utils import get_project_translation_by_slug

@before.all
def setup_env():
    world.language_code = 'en'
    world.project_slug = 'a-sample-project'

    world.browser = Client()
    world.edit_theme_url = django_url(reverse('project_sheet-instance-edit-related', args=(world.project_slug,)))

    create_project_translation(world.language_code, default_title=world.project_slug)


@step(r'I navigate to "(.*)"')
def navigate_to_url(step, url):
    full_url = django_url(url)
    world.response = world.browser.get(full_url, follow=True)
    assert(world.response.status_code == 200)

@step(r'I should see the message "(.*)"')
def check_response(step, message):
    assert 'h1' in world.response.content

@step(r'I want to change the themes of my project')
def project_sheet_change_theme(step):
    response = world.browser.get(world.edit_theme_url)
    assert(response.status_code == 200)

@step(r'I tag it with "(.*)"')
def project_sheet_tag_it(step, someTags):
    world.browser.post(world.edit_theme_url,
                       {'themes': someTags}
                       )

@step(r'My project is at least tagged with "(.*)"')
def project_sheet_is_tagged(step, someTags):
    project = get_project_translation_by_slug(world.project_slug, world.language_code)

    for tag in parse_tag_input(someTags):
        assert(tag in project.themes)

