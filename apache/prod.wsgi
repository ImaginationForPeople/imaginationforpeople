#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import site

site.addsitedir('/home/www/virtualenvs/imaginationforpeople.org/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'imaginationforpeople.settings'

sys.path.append('/home/www/virtualenvs/imaginationforpeople.org/')
sys.path.append('/home/www/virtualenvs/imaginationforpeople.org/imaginationforpeople/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# When running under mod_wsgi the cms page resolver (sometimes) ends up using
# the wrong monkey-pactched reverse function for URL resolution. It should use
# the one from localeurl, so that when it gets the CMS root page, the language
# prefix is present and it can remove it from the path before resolving the
# page. For instance, if the path is /fr/aboutus and we don't use the reverse
# function from localeurl, the cms will try too look for a page fr/aboutus, when
# it should look for aboutus.
import cms.utils.page_resolver
import localeurl.models
cms.utils.page_resolver.reverse = localeurl.models.reverse
