#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

from haystack.views import search_view_factory

import views
import ajax

urlpatterns = patterns('',
    #url(r'^$', views.homepage, name='i4p-index'),
    url(r'^homepage/ajax/slider/bestof/$', ajax.slider_bestof, name='i4p-homepage-ajax-slider-bestof'),
    url(r'^homepage/ajax/slider/latest/$', ajax.slider_latest, name='i4p-homepage-ajax-slider-latest'),
    url(r'^homepage/ajax/slider/commented/$', ajax.slider_most_commented, name='i4p-homepage-ajax-slider-commented'),

    url(r'^history/check_version/(?P<pk>[\d]+)$', views.VersionActivityCheckView.as_view(), name='history-check-version'),
    url(r'^search/', search_view_factory(view_class=views.SearchView), name='i4p-search'),
    url(r'^location/(?P<location_id>\d+)', views.LocationEditView.as_view(), name='i4p-location-edit'),
    url(r'^locations/$', views.LocationListView.as_view(), name='i4p-location-list'),
    url(r'^locations/missing/(?P<missing_field_name>\w+)$', views.LocationListView.as_view(), name='i4p-location-missing-list'),

)

