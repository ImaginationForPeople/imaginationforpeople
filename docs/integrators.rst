###########
Integration
###########

Overview and project structure
##############################

Integration consist mainly in building templates, stylesheets and javascript 
files out of design mockups using the project's application framework.

Project in structured in multiple sub-application:  project_sheet, tags, api, etc.

For each sub-application, we fill find multiple usefull paths :

* ``apps/APPNAME/templates/`` : where templates are located for sub-application APPNAME
* ``static/sass/APPNAME/`` : where SASS stylesheets are located for sub-application APPNAME
* ``static/js/APPNAME/``: where javascript files are located for 

File structure
##############

TODO: What is the policy towards file location ? Should integrators prefer
main project or apps ?


Templates
#########

Templates are located in the `̀apps/\*/templates`` directory.

They are simple and standard HTML files that include a special syntax of
`template tags` at locations where dynamic data should appear.


Stylesheets
###########

`I4P` uses Compass_ and Scss_.

When you are working on ``.scss`` files, you need to have compass
running to make sure the ``.css`` files are regenerated.

As a side note, we made the choice to **commit** ``.scss`` files to
prevent having to install Compass_ on the deployment server, so please
do.


Compass
=======

Installing
----------

To install Compass_, from the project root run::

  bundle install --path=vendor/bundle


Running
-------

To allow CSS (re)generation, use the following command while modifying
CSSes::

   cd static
   bundle exec compass watch

If compass crashes when trying to regenerate files you are still editing, can
try the following command::

   while true ; do bundle exec compass watch static ; done

To run a one-time compilation, use::

    bundle exec compass compile static


SCSS Mixins
###########

TODO: explain how re-usable variables & mixins are better than having title
sizes and common classes redefined everywhere.


Pre-defined CSS Classes
#######################

TODO: explain common classes for button, project cards, etc.


.. _Compass: http://compass-style.org/
.. _Scss: http://sass-lang.com/
