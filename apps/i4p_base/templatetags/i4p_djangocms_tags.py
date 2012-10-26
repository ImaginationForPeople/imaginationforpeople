from cms.templatetags.cms_tags import ShowPlaceholderById
from cms.models import Page
from django import template
register = template.Library()

#
class PopupPlaceholderById(ShowPlaceholderById):
    """
    same signature as show_placeholder, but displays as a notification in a 
    popup, and doesn't raise an exception if the page does not exist.
    """
    name = 'popup_placeholder_by_id'
    template = 'cms/placeholder_popup.html'
    def get_context(self, *args, **kwargs):
        try:
            return super(PopupPlaceholderById, self).get_context(*args, **kwargs)
        except Page.DoesNotExist:
            return {'content': ''}
        

register.tag('popup_placeholder', PopupPlaceholderById)