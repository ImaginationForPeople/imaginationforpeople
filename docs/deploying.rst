Deploying using fab
===================

To get a listing of everything you can do with current fabfile, call::

   fab -l

Available commands:
   * *build_env* :                Build the virtualenv
   * *check_or_install_logdir* :  Make sure the log directory exists and has righ...
   * *commonenv*      :          Base environment
   * *configure_webserver* :      Configure the webserver stack.
   * *deploy_bootstrap* :         Deploy the project the first time.
   * *fullupdate* :               Full Update the maincode and the deps
   * *install_buildeps* :         Will install commonly needed build deps for pip...
   * *install_webserver* :        Will install the webserver stack (only apache f...
   * *meta_full_bootstrap* :      For use on new, empty environnements
   * *prodenv* :                  production environment - NOT IMPLEMENTED YET
   * *reload_webserver* :         Reload the webserver stack.
   * *reloadapp* :                Touch the wsgi
   * *stagenv* :                  Stagging environment
   * *syncdb* :
   * *tests* :                    Run all tests on remote
   * *update* :                   Fast Update : project maincode
   * *update_requirements* :      update external dependencies on remote host
   * *venvcmd* :

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

   fab --user=yoursudouser stagenv meta_full_bootstrap

Update app main code and templates, update all dependencies, launch
syncdb, launch migrations, run all tests, reload app. (It will stop if
preceeding command fails so no app reloading if tests fail)::

   fab --user=yoursudouser stagenv fullupdate

Sames as above but without all the piping update (wich takes fabulous
amomunt of time). To be used for minor updates (without dependency
changes) - is much faster::

   fab --user=yoursudouser stagenv update

Pip update everything in the venv::

   fab --user=yoursudouser stagenv update_requirements

etc ...
