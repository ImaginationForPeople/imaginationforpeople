###########
Integration
###########

Integration consist mainly in building templates, stylesheets and javascript 
files out of design mockups using the project's application framework.


Project structure
#################

Overview
--------

The ImaginationForPeople project in structured in multiple sub-application: 
``project_sheet``, ``tags``, ``api``, etc.

For each sub-application, here called APPNAME, we fill find multiple usefull paths :

* ``apps/APPNAME/templates/APPNAME/`` : location for templates ;
* ``static/sass/APPNAME/`` : location for SASS stylesheets ;
* ``static/js/APPNAME/``: location for javascript files ;
* ``static/images/APPNAME/``: location for images files ;
* ``static/sprites/APPNAME/``: location for sprites files.


Within those paths, objects must be organized in the following way :

* ``./layout/*`` : files related to one of the layouts ;
* ``./page/*`` : files related to one of the pages ;
* ``./block/*`` : reusable parts of the pages ;
* ``./ajax/*`` : like blocks, but for asynchronously loaded content ;
* ``./emails/*`` : like pages, but for sent emails.

Instead of APPNAME, you may also find directories called ``i4p`` which contains
transversally reusable libraries of functions, components, constants definitions and such.


FIXME: objects names should be kept the same accross all these directories.

FIXME: draw a schema of inclusion between pages / layouts / etc.

FIXME: What is the policy towards file location ? 

FIXME: Should integrators prefer main project or apps ?


An example
----------

* ``apps/project_sheet/templates/project_sheet/block/memberlist_square.html`` : the javascript file
* ``static/sass/project_sheet/block/memberlist_square.scss`` : the CSS file
* ``static/js/project_sheet/block/memberlist_square.js`` : the javascript file


HTML Templates
##############

Templates are located in the `̀`apps/APPNAME/templates/APPNAME/`` directory.

They are simple and standard HTML files that include a special syntax of
`template tags` at locations where dynamic data should appear.

FIXME: add a link to django reference docs for template tags

FIXME: explain where are the usable modules / templates tags

FIXME: explain template structure


Template structure overview
---------------------------

* Header comment
* Requirements
* Sekizai blocks
* Template content


Header comment
--------------

FIXME: required usable variables

FIXME: block/ajax/page/etc purpose


Requirements
------------

FIXME: add an example of html template requirements

FIXME: explain known modules


Sekizai blocks
--------------

FIXME: list available blocks : js / footer_js / css

FIXME: explain sekizai bugs : whitespaces / tags & blocks

FIXME: add an example of sekizai block in html template


Template content
----------------

FIXME: explain things about closed tags 

FIXME: explain things about block definition in layouts / pages



Stylesheets
###########



Javascript
==========


FIXME: explain performance issues depending on where the code is loaded  (synchrone, asynchrone, blocking, etc)

FIXME: explain how to separate code from HTML with meaningfull data-* attributes

FIXME: explain how to translate content in Javascript (using {% trans 'machin' %} as HTML data-attributes parameters...)



Graphic assets
==============



Stylesheets
===========

FIXME: explain that things are either specific to a layout, to a page, or to a block  

Anti-collision rules
--------------------

FIXME: explain what is a collision, and how to prevent them.


SCSS Mixins
###########

TODO: explain how re-usable variables & mixins are better than having title
sizes and common classes redefined everywhere.


Pre-defined CSS Classes
#######################

TODO: explain common classes for button, project cards, etc.


