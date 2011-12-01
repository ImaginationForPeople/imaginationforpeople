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
from django.test.client import Client

from lettuce import before, step, world
from lettuce.django import django_url

@before.all
def set_browser():
    world.browser = Client()

@step(r'I navigate to "(.*)"')
def navigate_to_url(step, url):
    full_url = django_url(url)
    world.response = world.browser.get(full_url, follow=True)
    assert(world.response.status_code == 200)

@step(r'I should see the message "(.*)"')
def check_response(step, message):
    assert 'h1' in world.response.content
