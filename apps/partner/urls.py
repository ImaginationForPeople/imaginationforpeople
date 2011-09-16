#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
     url(r'^$', views.PartnerListView.as_view(), name='partner-list'),
     url(r'^(?P<slug>[-\w]+)/$', views.PartnerDetailView.as_view(), name='partner-detail'),
)





