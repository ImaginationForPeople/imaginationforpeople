====================================
Setting-up a development environment
====================================

Database
========

Once you've created a database for the project (such as 'imaginationforpeople'),
edit site_settings.py and make sure your database connection parameters are
correct. Then you need to initialize your database with these commands::

    python manage.py syncdb
    python manage.py migrate
    python manage.py check_permissions

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

Social authentication
=====================

This section describes how to setup your instance of the application to support
authentication against social services.

Services configuration
----------------------

For each supported authentication service, you need an account with that service
and you need to use that account to create and configure an *application* using
their web interface. Each service will provide you with a pair of ID/Key and
secret.

Most services requires that you provide one or more URLs pointing to your
site. In development you can't use the real site URL but you can make up one.  It
doesn't need to be based on a valid hostname but it needs to look valid, so
``http://127.0.0.1:8000`` won't work but something like
``http://i4p-dev.com:8000`` will do. You'll need to configure your machine so
that your site URL points to your local instance. On Unix systems you can do
this by adding an entry to ``/etc/hosts``::

    127.0.0.1   i4p-dev.com

In the subsequent sections we assume that the hostname pointing to your
development machine is ``i4p-dev.com`` but you can use another hostname if you
wish.


Facebook
^^^^^^^^

Go to https://developers.facebook.com/ and create a new app. You'll need to
enter a site URL: ``http://i4p-dev.com:8000``.

Google
^^^^^^

Google offers several authentication options. We use 
`OAuth2 <http://code.google.com/apis/accounts/docs/OAuth2.html>`_. Go to
https://code.google.com/apis/console and create a new Client ID.  Redirect URIs
should contain ``http://i4p-dev.com:8000/member/complete/google-oauth2/`` and
JavaScript origins should contain ``https://i4p-dev.com``.

Twitter
^^^^^^^

Go to https://dev.twitter.com/k and create a new app. Your callback URL should
be ``http://i4p-dev.com:8000/``.

LinkedIn
^^^^^^^^

Go to https://www.linkedin.com/secure/developer and add a new application. 

OpenID
^^^^^^

No configuration is required for basic OpenID authentication.

Local configuration
-------------------

Then you need to enter an ID/Key and secret pair for each authentication service
in ``site_settings.py`` (remember that you should never store this file into
version control).


.. code-block:: python

    # Social auth
    FACEBOOK_APP_ID              = 'XXXXXXXXX'
    FACEBOOK_API_SECRET          = 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'

    TWITTER_CONSUMER_KEY         = 'XXXXXXXXXXXX'
    TWITTER_CONSUMER_SECRET      = 'XXXXXXXXXXXXXXXXXXXX'

    GOOGLE_OAUTH2_CLIENT_KEY     = 'XXXXXXXX.apps.googleusercontent.com'
    GOOGLE_OAUTH2_CLIENT_SECRET  = 'XXXXXXXXXXXXXXX'

    LINKEDIN_CONSUMER_KEY        = 'XXXXXXXX'
    LINKEDIN_CONSUMER_SECRET     = 'XXXXXXXXXXXX'
