#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import site

site.addsitedir('/home/webapp/virtualenvs/prod.imaginationforpeople.com/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'imaginationforpeople.settings'

sys.path.append('/home/webapp/virtualenvs/prod.imaginationforpeople.com/')
sys.path.append('/home/webapp/virtualenvs/prod.imaginationforpeople.com/imaginationforpeople/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
