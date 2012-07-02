#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

import views
import ajax

urlpatterns = patterns('',
    url(r'^$', views.homepage, name='i4p-index'),
    url(r'^homepage/ajax/slider/bestof/$', ajax.slider_bestof, name='i4p-homepage-ajax-slider-bestof'),
    url(r'^homepage/ajax/slider/latest/$', ajax.slider_latest, name='i4p-homepage-ajax-slider-latest'),
    url(r'^homepage/ajax/slider/commented/$', ajax.slider_most_commented, name='i4p-homepage-ajax-slider-commented'),
)

