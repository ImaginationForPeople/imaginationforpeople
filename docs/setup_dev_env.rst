====================================
Setting-up a development environment
====================================

Compass
=======

Installing
----------

Add this at the end of your "bin/activate" script::

    export GEM_HOME="$VIRTUAL_ENV/gems"
    export GEM_PATH=""
    export PATH="$PATH:$GEM_HOME/bin"

then, source it again and run::

      gem install compass rb-inotify


Running
-------

To allow CSS (re)generation, use the following command while modifying
CSSes::

   compass watch media/

To run a one-time compilation, use::

   compass compile media

