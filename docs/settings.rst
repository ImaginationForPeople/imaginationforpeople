.. _application-configuration:

Application Configuration
#########################

Before running the app, you need to configure it through the
:file:`site_settings.py` file. While some of theses settings are easy
to understand, some others are not that trivial. This section is here
to guide through the laters.

If this is the first time you're configuring this app, you should
start by copying :file:`site_settings.py.sample` to
:file:`site_settings.py`.

Basic settings
==============

Database
--------

You need to define at least an :keyword:`ENGINE`, :keyword:`NAME` and
:keyword:`USER` for the database to be configured. For a typical
PostGreSQL configuration, that would look like this::

  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
          'NAME': 'imaginationforpeople', # Or path to database file if using sqlite3.
          'USER': 'imaginationforpeople', # Not used with sqlite3.
          'PASSWORD': 'plop', # Not used with sqlite3.
          'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
          'PORT': '', # Set to empty string for default. Not used with sqlite3.
      }
  }


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

You can also use your zeroconf (avahi, bonjour) host, such as
mymachine.local.

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


Forum
=====

.. code-block:: python
    ASKBOT_URL = 'forum'
    
The configuration of the forum is delegated to django-livesettings : /[ASKBOT_URL]/settings/


Reference configuration
=======================

Site configuration template:

.. literalinclude:: ../site_settings.py.sample
   :language: python
   :linenos:

Common configuration:

.. literalinclude:: ../settings.py
   :language: python
   :linenos:
