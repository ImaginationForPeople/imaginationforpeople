from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

import views

urlpatterns = patterns('',
    url(r'^$', views.homepage, name='i4p-index'),
)

