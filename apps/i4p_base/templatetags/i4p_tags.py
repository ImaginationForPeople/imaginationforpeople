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
import re

from django import template
from django.conf import settings
from django.core import urlresolvers
from django.utils import translation
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def url_target_blank(value): 
    return re.sub("<a([^>]+)(?<!target=)>",'<a target="_blank"\\1>', value)
url_target_blank.is_safe = True

@register.filter
@stringfilter
def chlocale(url, locale):
    """
    Changes the URL's locale prefix if the path is not locale-independent.
    Otherwise removes locale prefix.
    XXX: Taken from localeurl (https://bitbucket.org/carljm/django-localeurl/)
    """
    def strip_script_prefix(url):
        """
        Strips the SCRIPT_PREFIX from the URL. Because this function is meant for
        use in templates, it assumes the URL starts with the prefix.
        """
        assert url.startswith(urlresolvers.get_script_prefix()), \
            "URL must start with SCRIPT_PREFIX: %s" % url
        pos = len(urlresolvers.get_script_prefix()) - 1
        return url[:pos], url[pos:]
        
    def strip_path(path):
        """
        Separates the locale prefix from the rest of the path. If the path does not
        begin with a locale it is returned without change.
        """
        SUPPORTED_LOCALES = dict(
            (code.lower(), name) for code, name in settings.LANGUAGES)
        # Issue #15. Sort locale codes to avoid matching e.g. 'pt' before 'pt-br'
        LOCALES_RE = '|'.join(
            sorted(SUPPORTED_LOCALES.keys(), key=lambda i: len(i), reverse=True))
        PATH_RE = re.compile(r'^/(?P<locale>%s)(?P<path>.*)$' % LOCALES_RE, re.I)
        
        check = PATH_RE.match(path)
        if check:
            path_info = check.group('path') or '/'
            if path_info.startswith('/'):
                return check.group('locale'), path_info
        return '', path

    _, path = strip_script_prefix(url)
    _, path = strip_path(path)
    
    old_locale = translation.get_language()
    translation.deactivate_all()
    translation.activate(locale)
    try:
        url =  locale + path
    finally:
        translation.activate(old_locale)

    return '/' + url
    
chlocale.is_safe = True
