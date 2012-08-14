#############################
Synching with production data
#############################

That's just a three coffees step.

First, make sure you have fabric_ installed and run::

  fab prodenv get_database

*...first coffee...*

then::

  fab devenv restore_database

*...second coffee...*

and finally, get the media and clear the cache::

  scp -r web@i4p-prod.imaginationforpeople.org:/home/www/virtualenvs/imaginationforpeople.org/imaginationforpeople/media/uploads media/
  ./manage.py ikflush

*...third coffee, you're done!*

.. _fabric: http://fabfile.org
