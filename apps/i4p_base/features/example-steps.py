from lettuce import before, step, world
from lettuce.django import django_url

from nose.tools import assert_equals

from django.test.client import Client

@before.all
def set_browser():
    world.browser = Client()

@step(r'I access the url "(.*)"')
def access_url(step, url):
    full_url = django_url(url)
    print full_url
    response = world.browser.get(full_url)

@step(r'I see the header "(.*)"')
def see_header(step, text):
    pass
