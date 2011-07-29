************
Server Setup
************

This document assumes the server is running the following OS :

Debian GNU/Linux 6.0 (Squeeze) / AMD64

We also assume to have a user called **web** which handles the Django
application.

First deployement
*****************

Make sure the **web** user can access the main git repository on the
developement server using a RSA key.

To install for the first time on a production environement, run::

   fab prodenv meta_full_bootstrap

Web servers configuration
*************************

======
Apache
======

We run *Django* using Apache2/WSGI.

The following changes are still needed by hand before deploying, in
'ports.conf'. Replace::
	
	NameVirtualHost *:80
	Listen 80

by::

	NameVirtualHost *:8281
	Listen 8281
	

Production configuration file
=============================

.. literalinclude:: ../apache/www.imaginationforpeople.org
   :linenos:

Staging configuration file
==========================

.. literalinclude:: ../apache/staging.imaginationforpeople.org
   :linenos:

=====
Ngnix
=====

Static files are handled by Nginx.


Database server configuration
*****************************

==========
Postgresql
==========

Access control
==============

From the file '/etc/postgresql/8.4/main/pg_hba.conf', update the
following line::

  # "local" is for Unix domain socket connections only
  local   all         all                       ident

with::

  # "local" is for Unix domain socket connections only
  local   all         all                       md5


User password
=============

Change the 'imaginationforpeople' user password using the following
commands::

  web@i4p-prod:~$ sudo su postgres -c psql template1
  postgres=# ALTER USER imaginationforpeople with PASSWORD 'THE-NEW-PASSWORD';


Setting-up the app
==================

As **web**::

	web@i4p-prod:~$ mkdir virtualenvs
	web@i4p-prod:~$ cd virtualenvs/
	web@i4p-prod:~/virtualenvs$ virtualenv --no-site-packages imaginationforpeople.org

then clone the app::

	web@i4p-prod:~/virtualenvs$ cd imaginationforpeople.org/
	web@i4p-prod:~/virtualenvs/imaginationforpeople.org$ git clone ssh://webapp@code.imaginationforpeople.com/var/repositories/imaginationforpeople.git
	

