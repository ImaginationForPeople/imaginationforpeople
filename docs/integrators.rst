===========
Integration
===========

Integration consist mainly in building templates, stylesheets and javascript 
files out of design mockups using the project's application framework.


Project structure
=================

Overview
--------

The ImaginationForPeople project in made of multiple sub-applications: 
``project_sheet``, ``tags``, ``api``, etc.

Each of these sub-applications is a aggregate of many things of various types, called *components*.

The main focus within the project structure we choose, is to keep each component as reusable as possible.

To achive this goal, we agreed to follow those simple rules for components :
 - they must be as **context-free** as possible,
 - they must be as **simple** as possible,
 - they must be **consistent**.
 
Let's explain these three concepts.


Context free
````````````

FIXME: explain what context free means


Simple
``````

FIXME: explain that complex things are hard to maintain

FIXME: explain that it is better to split into multiple parts (that can be composed together)

FIXME: explain that it makes less dependencies (see consistent)


Consistence
```````````

FIXME: explain the notion of dependencies

 




Where to put components
-----------------------

Components paths
````````````````


For each sub-application, here called APPNAME, we fill find multiple usefull paths :

* ``apps/APPNAME/templates/APPNAME/`` : location for templates ;
* ``static/sass/APPNAME/`` : location for SASS stylesheets ;
* ``static/js/APPNAME/``: location for javascript files ;
* ``static/images/APPNAME/``: location for images files ;
* ``static/sprites/APPNAME/``: location for sprites files.


FIXME: What is the policy towards file location ? 

FIXME: Should integrators prefer main project or apps ?


Components roles
````````````````

These components could fit in one of the following categories : *layout*, *page*, *block*
*ajax*, *emails*. 

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


An example
----------

* ``apps/project_sheet/templates/project_sheet/block/memberlist_square.html`` : the javascript file
* ``static/sass/project_sheet/block/memberlist_square.scss`` : the CSS file
* ``static/js/project_sheet/block/memberlist_square.js`` : the javascript file
* ``static/sprites/project_sheet/...`` : the pictures files
* ``static/images/project_sheet/...`` : the sprites files

FIXME: display the 3 trees in parallel for a given example



HTML Templates
==============

Overview
--------

Templates are simple and standard HTML files that include a special syntax of
`template tags` at locations where dynamic data should appear.

They are located in the ``apps/APPNAME/templates/APPNAME/`` directory.


FIXME: add a link to django reference docs for template tags

FIXME: explain where are the usable modules / templates tags

FIXME: explain template structure


Template structure overview: 

* Header comment
* Requirements
* Assets blocks
* Template content


Header comment
--------------

The header comment is here to define why the component you are writing is made
for. 

The header comment should something meaningful for later developpers. 
Usually it answers the following questions :

* Is it a page/block/layout/etc ?
* What does it display ?
* Does it have any special use conditions ? (ex: it relies on the bootstrap CSS grid...)
* What are its parameter variables ? 

It is also hightly recommended write a usage example of the block if it accepts parameters.


FIXME :explain parameters variables naming for templates

FIXME: add an example of well-writen header.


Requirements
------------

FIXME: add an example of html template requirements

FIXME: explain known modules




Assets blocks
-------------

Assets blocks is where a HTML template can declare the stylesheet or javascript files it requires.
Assets blocks relies on the *sekizai* django module.

A simple example of assets blocks in a html template::

  ... HTML template header
  ... HTML template requirements
  
  {% addtoblock "footer_js" %}
  <script type="text/javascript">
  $.getScript(I4P_STATIC_URL+"js/project_sheet/block/toolbar.js");  
  </script>
  {% endaddtoblock %}

  {% addtoblock "css" %}
  <link type="text/css" rel="stylesheet" href="{{ STATIC_URL }}css/project_sheet/block/toolbar.css" />
  {% endaddtoblock %}


Available zones (FIXME: make a link to page blocks)

Available blocks for sekizai : **css**, **js**, **footer_js** .

The "css" block
````````````````

FIXME: explain where it is (html example)


The "js" block
``````````````

FIXME: explain where it is in the pages

FIXME: explain js loading performance/blocking issues of putting things into the header


The "footer_js" block
`````````````````````

FIXME: explain that footer_js will be evaluated after the page content,

FIXME: explain how to use async loading with jquery require ;)


Sekizai problems
````````````````
Actually, there is a problem with the current sekizai system, instead of comparing string meaning (ie: with a *abstract syntaxic tree*), it compares
strings, **not even taking in account whitespaces and indentation**.

For instance, the following block ::

  {% addtoblock "js" %}
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.growfield.js"></script>
  {% endaddtoblock %}

is considered different from ::

  {% addtoblock "js" %}
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.growfield.js">
  </script>
  {% endaddtoblock %}

or from ::

  {% addtoblock "js" %}<script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.growfield.js"></script>{% endaddtoblock %}


A quick and dirty work-around
`````````````````````````````

To circumvent the previously stated problem, we suggest that instead of writing ::


  {% addtoblock "js" %}
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.growfield2.js"></script>
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.js"></script>
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.growfield.js"></script>
  {% endaddtoblock %}

  
We should write::


  {% addtoblock "js" %}
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.growfield2.js"></script>
  {% endaddtoblock %}
    
  {% addtoblock "js" %}
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.js"></script>
  {% endaddtoblock %}
    
  {% addtoblock "js" %}
  <script type="text/javascript" src="{{ STATIC_URL }}js/jquery/jquery.jeditable.growfield.js"></script>
  {% endaddtoblock %}

  


Template content
----------------

Template content is where you write the HTML.

Rules
`````

.. warning:: make sure that **any opened HTML tag** in the content **is closed in the same file**.

.. warning:: 

  **Never reference any static image or sprite** (you'd be striken by a lightning imediatly).

.. warning:: 

  **Never put any javascript content** in there, neither as a sekizai block, nor mixed within HTML
  (a troll would come out of its cave to eat you while you sleep).


Sekizai block definitions
````````````````````````` 

FIXME: explain things about block definition in layouts / pages


HTML "id" attributes limitations
````````````````````````````````

FIXME: Explain issues of non-reusability caused by fixed identifiers. 
FIXME: Explain how to overcome id attibute naming by using unique_tag & counters



Javascript
==========


Clean javascript
----------------

FIXME: explain how to separate code from HTML with meaningfull data-* attributes

FIXME: explain how to translate content in Javascript (using {% trans 'machin' %} as HTML data-attributes parameters...)

FIXME: do not mix CSS and JS. Except for dynamically positionning elements, you should be enabling/disabling CSS classes instead.

FIXME: explain how to use jquery signals/bindings/triggers.


JSLint your code
----------------


Javascript performance
----------------------

FIXME: explain performance issues depending on where the code is loaded  (synchrone, asynchrone, blocking, etc)


Graphic assets
==============



Stylesheets
===========

FIXME: explain that things are either specific to a layout, to a page, or to a block  

Anti-collision rules
--------------------

FIXME: explain what is a collision, and how to prevent them.


Variables naming
----------------

FIXME: explain schema for naming variables and constants


SCSS Mixins
-----------

TODO: explain how re-usable variables & mixins are better than having title
sizes and common classes redefined everywhere.

TODO: explain how scss mixins work. (add link to an article)

FIXME: document existing mixins with screenshot and code examples


Site-wide constants
```````````````````

This file, located in ``PROJECT_ROOT/static/sass/i4p/_constants``, contains definitions for
all site-wide constants (font sizes, padding sizes, etc.).

FIXME: explain available constants (padding, margin, font-sizes, etc.)

.. warning ::

  If you are modifing these constant values, you're probably wrong.



Rules
-----

.. warning ::

  Do not use define values in pixels (or hex/rgb colors) or any other kind 
  of locally hardwritten value in you CSS. **Use I4P constants instead**.



Naming constants
----------------

Urls
----

FIXME: talk about image-urls & relative paths


Sprites
-------

FIXME: sprites are great

FIXME: beware css name collisions & bad namespaces



Very important files
---------------

Styles.scss
```````````

The ``PROJECT_ROOT/static/styles.scss`` is the main CSS file, called before anything else on any page.

**It must remain minimal**. As such, it only has to contain the text size definition for the root element.

.. warning::

  If you are doing a change in this file, you are probably wrong. Re-read the Stylesheets section.



Some pre-defined CSS Classes
-----------------------

TODO: explain common classes for button, project cards, etc. Add screenshot + code examples


Compass internals
=================


FIXME: Explain how compass works, explain config.rb & paths parameters

FIXME: explain post-processing for REM units

FIXME: explain post-processing for sprite identifiers


Internet Explorer compatibility
===============================

FIXME: explain what we aim.


Other references
=================

FIXME: integrate the following link in the doc, with real code examples : https://dev.imaginationforpeople.org/redmine/issues/1170 
    

