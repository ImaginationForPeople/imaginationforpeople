#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import site

site.addsitedir('/home/webapp/virtualenvs/staging.imaginationforpeople.org/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'imaginationforpeople.settings'

sys.path.append('/home/webapp/virtualenvs/staging.imaginationforpeople.org/')
sys.path.append('/home/webapp/virtualenvs/staging.imaginationforpeople.org/imaginationforpeople/')
sys.path.append('/home/webapp/virtualenvs/staging.imaginationforpeople.org/imaginationforpeople/apps/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
