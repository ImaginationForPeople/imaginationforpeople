=======
Testing
=======

The code base includes two distinct sets of tests.  One is based on the default
Django testing framework. There's a known issue with these tests whereby it's 
not possible to use Django test client to simulate HTTP requests.  The other 
set of tests is based on Lettuce_, a Python BDD testing tool.  The recommended 
way to test HTTP requests is to use Lettuce.

Classic Django tests
====================

You can run these tests with this command::
    
    python manage.py test

By default, they run against a PostgreSQL database, which can be quite slow. If 
you wish to speed up execution of these tests, you can run the test suite 
against an in-memory SQLite database by adding something like this after your 
database definition in your site_settings.py::

    import sys
    if 'test' in sys.argv:
        DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

However please be aware that the team has experienced differences of behaviors
between running the tests against a PostgreSQL database and a SQLite database.
By precaution, fefore publishing your changes you should run the tests with
PostgreSQL.

Lettuce BDD behaviors
=====================

The set of Lettuce_ behaviors can be executed with this command::

    python manage.py harvest

By default this will start a built-in webserver and you might notice that the
command never returns. You can terminate it with Control-C. In order to avoid
this issue you can disable the built-in server with the ``-S`` switch::

    python manage.py harvest -S

You can run behaviors only for a specific app with a command such as::

    python manage.py harvest -S apps/member/features

.. _`Lettuce`: http://lettuce.it/
