Coders
######

Mailing list: http://lists.imaginationforpeople.org/cgi-bin/mailman/listinfo/dev

.. toctree::
   :maxdepth: 2

   testing.rst
   localization.rst

Creating a database migration

Change the models.py file in an app.

Create a migration file for generation N+1:
./manage.py schemamigration app_name --auto 
Actually update the database
./manage.py migrate app_name 
