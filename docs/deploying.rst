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
