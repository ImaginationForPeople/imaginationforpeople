Deploying using fab
===================

To get a listing of everything you can do with current fabfile, call::

   fab -l

Available commands:
    * *app_fullupdate*:     Full Update: maincode and dependencies
    * *app_install*:        (Re)install app to target server
    * *app_update*:         Fast Update: don't update requirements
    * *bootstrap_full*:     Install system tools, create venv and install app
    * *bootstrap_venv*:     Create the virtualenv and install the app
    * *database_download*:  Dumps and downloads the database from the target serv...
    * *database_dump*:      Dumps the database on remote site
    * *database_restore*:   Restores the database to the remote server
    * *devenv*:             [ENVIRONMENT] Developpement (must be run from the vir...
    * *mirror_prod_media*:  Mirror the production media (pictures, ...) the targe...
    * *prodenv*:            [ENVIRONMENT] Production
    * *stagenv*:            [ENVIRONMENT] Staging


TODO: update!

Basic usage
-----------

Sample command::

  fab --user=yoursudouser environnement command command2 command3

Parts:
  * --user=yoursudouser : Replace by your user with sudo rights on the target system. exemple --user=pmironov
  * environnement : Special command that sets target env parameters, mainly *stagenv* or *prodenv*
  * command command2 etc ... : one or more commands. Will be run sequentially. The fabfile provides meta commands thought and you'll probably be useing one at a time anyway.


Examples
--------

Full environnement bootstrap and app bootstrap on staging env
(Requires a debian lenny environnement with a webapp user and python
installed)::

   fab --user=yoursudouser stagenv bootstrap_full

Update app main code and templates, update all dependencies, launch
syncdb, launch migrations, run all tests, reload app. (It will stop if
preceeding command fails so no app reloading if tests fail)::

   fab --user=yoursudouser stagenv app_fullupdate

Sames as above but without all the piping update (wich takes fabulous
amomunt of time). To be used for minor updates (without dependency
changes) - is much faster::

   fab --user=yoursudouser stagenv app_update

etc ...


Before you deploy a release, stage locally
------------------------------------------

Before a major release in prod (this is usually not needed for hotfixes), you 
need to test locally the our css and javascript compression will not crash and 
burn on the server.  There are many reasons why it can break, and you wouldn't 
see it in a development environment.

Make sure you have EVERYTHING commited under /static, as the following WILL 
mangle your static directory
   
   Add COMPRESS_ENABLED = True in your site_settings.py
   
   ./manage.py collectstatic

   ./manage.py runserver --insecure

Run your tests...

Once done:

   Remove COMPRESS_ENABLED = True in your site_settings.py

   Run git clean -f -d static
   
Deploying on production server
______________________________

As this is typicaly critical, here is a guide on how to put the latest release on the production server.

* Merge current release branch into upstream/develop and upstream/master. Make sure your develop and master are sync with upstream server::

   me@mylocalmachine/i4p$ git flow release finish release_name

* push these updates on upstream repository::
   
   me@mylocalmachine/i4p$ git push upstream
 
* put production server on maintenance by commenting out these lines on the apache conf file:: 
   
   nano /etc/apache2/sites-available/www.imaginationforpeople.org
Comment out the following lines::
   
   #RewriteCond %{REQUEST_URI} !/maintenance/
   #RewriteCond %{REMOTE_HOST} !^88\.185\.104\.130
   #RewriteCond %{REMOTE_HOST} !^213\.243\.180\.2
   #RewriteCond %{REMOTE_HOST} !^82\.225\.123\.163
   #RewriteRule $ /maintenance/maintenance.htm [R=302,L]

* dump production database::
   
   me@mylocalmachine/i4p$ fab prodenv database_dump

Then, 2 scenarios:

1 Automatic update using fab
____________________________

* run full update prod server::

   mylocalmachine/i4p$ fab prodenv app_fullupdate

If everything went well, go to last step, else proceed to scenario 2. In case of a fail, you generally just need to checkout on the production server, and then lauch again the fab script.

2 Manual update
_______________

The most generic way to update manually is the following::

   web@prodserver$ git fetch origin
   web@prodserver$ git merge origin/master
   web@prodserver$ pip install -r requirements.txt
   web@prodserver$ ./manage.py syncdb --migrate
   web@prodserver$ ./manage.py collectstatic
   web@prodserver$ cd static/
   web@prodserver/static/$./build.sh
   
On specific cases, there might be other manual work that will be documented (for example, tricky migrations)

3 Last steps 
____________

When everything on production server is up to date with master upstream repository, you just have to reload apache::
   
   sudo /etc/init.d/apache2 reload

Then put main site back online by commenting back relevant lines

