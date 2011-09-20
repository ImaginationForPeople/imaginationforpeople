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
from dozer import Dozer
application = django.core.handlers.wsgi.WSGIHandler()
application = Dozer(application)
