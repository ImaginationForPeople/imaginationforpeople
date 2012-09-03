#-- encoding: utf-8 --
from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<tag>[\s\w\d-]+)$', views.TagPageView.as_view(), name='tag-view'),
    url(r'^(?P<tag>[\s\w\d-]+)/wiki/edit$', views.TagEditWikiView.as_view(), name='wiki-edit'),
)

def get_pattern(app_name="tags", namespace="tags"):
    """
    Every url resolution takes place as "tags:view_name".
    """
    return urlpatterns, app_name, namespace
