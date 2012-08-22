============
Localization
============

Updating translation files
==========================

By hand
-------

``manage.py makemessages`` won't work because apps are located under the
``apps`` directory. Instead you need to use ``django-admin.py`` from each app
directory.  For instance to generate .po files (translation source files) for
the member app::

    cd apps/member/
    django-admin.py makemessages -a -e html,txt

Similarly, to regenerate .mo files (compiled translation files), you do this::

    cd apps/member/
    django-admin.py compilemessages

Automatically
-------------

Alternatively, fabric tasks are available to do this on all translated apps for you::

    fab devenv make_messages

Do your translation work, and then run::

    fab devenv compile_messages
