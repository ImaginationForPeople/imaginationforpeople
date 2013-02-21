====================================
Setting-up a development environment
====================================

Bootstrapping an environment automatically
==========================================

There is a fabfile to help you.  The following commands should install and setup
 everything on debian based Linux distributions.  All you need is fabric installed::

  wget https://raw.github.com/ImaginationForPeople/imaginationforpeople/master/fabfile.py
  fab devenv bootstrap_venv
  fab devenv bootstrap_full

Grabbing a copy of the production environnement
-----------------------------------------------
Working on a copy of the production database is the best way to avoid accidentally 
breaking stuff::

  fab prodenv database_download
  fab devenv database_restore

If you ran the above successfully, you can ignore the rest of this page.

Bootstrapping an environment
============================

First, you need to setup an isolated developement environment for the
python apps using virtualenv_. If you don't have virtualenv_, you can
install it using your package manager such as *apt* if you're on
debian::

  apt-get install virtualenv
  virtualenv --no-site-packages i4p-env

Since we rely on a few Ruby_ tools, we recommend to use a ruby-specific
environment management tool like rbenv or rvm. Otherwise simply add the
following lines to your :file:`bin/activate` script to be able to use gems_::

  export GEM_HOME="$VIRTUAL_ENV/gems"
  export GEM_PATH=""
  export PATH="$PATH:$GEM_HOME/bin"

Then, enters the environment::

  cd i4p-env && source bin/activate

Your prompt should update to something like (note the prefix)::

  (i4p-env)glibersat@carpe:~/Source/i4p-env

.. warning::

  For all next steps, you need to be in an activated environment.


Getting the code
================

Once you're in your virtualenv directory, use::

  git clone https://github.com/ImaginationForPeople/imaginationforpeople.git
  cd imaginationforpeople
  git branch --track develop origin/develop
  git checkout develop

then, change directory to :file:`imaginationforpeople` and fetch the
dependencies using::

  pip install -U -r requirements.txt

*It may be the right to fetch a cup of coffee! :-)*

.. note::

  From now on, the ``imaginationforpeople`` directory will be called **the project root** (or **PROJECT_ROOT**).


Populating the Database
=======================

You need to configure a database server (PostGreSQL_ is recommended,
see how to configure it in the :ref:`database-server-configuration`
section) and create a database for the project (such as
'imaginationforpeople').

.. warning::

   If you haven't configured your :file:`site_settings.py` yet, jump
   to :ref:`application-configuration` before going on.

Then you need to initialize your database with these commands::

    python manage.py syncdb --all
    python manage.py migrate --fake
    python manage.py check_permissions

Django will prompt for a user creation, this is always a good idea to say *yes*::

     You just installed Django's auth system, which means you don't have any superusers defined.
     Would you like to create one now? (yes/no): **yes**


Feeding initial data
====================

While we'd like the app to work out of the box, a few maual steps are still needed.

Site declaration
----------------

You need to declare at least one website that matches your site's
production name. This simplest way is to go through a python shell::

  ./manage.py shell_plus
  site = Site.objects.get(id=1)
  site.domain = "imaginationforpeople.org"
  site.save()
  exit()


Default CMS templates
---------------------

We still have a few hardcoded templates that refer to specific CMS
pages. Therefore, you need to create them so the url lookups work.

First, run the server using::

  ./manage.py runserver

Then login to the admin panel (http://localhost:8000/admin/) using the
user you've just created.

Scroll down to the :guilabel:`Cms` section and click :guilabel:`Add`.

The following pages are required: **homepage**, **about_us**, **manifesto** and
**ipmedia**.

So, for each of these names, do the following:

#. Create a page
#. Edit it and in *Advanced parameters*, set the **id** to its name (i.e. *homepage*)
#. If this is the **homepage**, select "I4PBase App" as **Application**
#. Go back to the page listing and check *published*

Once you're done, restart the server.


.. _virtualenv: http://www.virtualenv.org/
.. _Ruby: http://www.ruby-lang.org/
.. _gems: http://rubygems.org/
.. _PostGreSQL: http://www.postgresql.org/


Compass and assets management
=============================

The `I4P` project uses many pretty features for developpers, like SCSS_, CSS-Sprites for icons, etc and we decided 
to use the Compass_ tool to help us do it automagically.

Thus, you will need to (re)generate assets (pictures, stylesheets, etc) to have a fully functional web site.


Installing compass
------------------

There are fabric tasks to make this easier (if you didn't already run fab devenv
 bootstrap_full):

Setup rbenv::

  fab devenv install_rbenv

Setup compass::
  fab devenv install_compass

Manually, to install Compass_, first make sure you have ruby and the bundle gem installed (the prefered way is to use rbenv_).

Then, from the project root run::

  bundle install --path=vendor/bundle


Automatically generating assets
-------------------------------


To do one-time compilation of assets, use the following command ::

  cd static && bundle exec compass compile static

  
To make an automaticall assets (re)generation when you edit files, use the following command while modifying
CSSes::

   cd static && bundle exec compass watch

   
Depending on your system environment, compass may crash when trying to regenerate files you are still editing.
The following command can be a work-around ::

  cd static && while true ; do bundle exec compass watch static ; done


And finally, to delete all generated assets, simply type ::

  cd static && while true ; do bundle exec compass clean

  
Instead of those complex command lines, you can also use the equivalent helper scripts (from the static/ directory):
``build.sh``, ``watch.sh``, ``clean.sh``.
    
.. _Compass: http://compass-style.org/
.. _Scss: http://sass-lang.com/
.. _RbEnv: https://github.com/sstephenson/rbenv