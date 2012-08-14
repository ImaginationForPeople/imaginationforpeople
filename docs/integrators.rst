###########
Integrators
###########

File structure
##############

TODO: Where to put files? Project or App?

Templates
#########

TODO

Stylesheets
###########

`I4P` uses Compass_ and therefore Scss_.

When you are working on ``.scss`` files, you need to have compass
running to make sure the ``.css`` files are regenerated.

As a side note, we made the choice to **commit** ``.scss`` files to
prevent having to install Compass_ on the deployment server, so please
do.

Compass
=======

Installing
----------

To install Compass_, run::

  gem install compass rb-inotify

Running
-------

To allow CSS (re)generation, use the following command while modifying
CSSes::

   compass watch static/

To run a one-time compilation, use::

   compass compile static


.. _Compass: http://compass-style.org/
.. _Scss: http://sass-lang.com/
