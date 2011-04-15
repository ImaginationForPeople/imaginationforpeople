import re

from django import template

register = template.Library()

def url_target_blank(value): 
    return re.sub("<a([^>]+)(?<!target=)>",'<a target="_blank"\\1>', value)

url_target_blank.is_safe = True
url_target_blank = register.filter(url_target_blank)
