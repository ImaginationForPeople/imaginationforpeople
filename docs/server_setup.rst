============
Server Setup
============

This document assumes the server is running the following OS :

Debian GNU/Linux 6.0 (Squeeze) / AMD64

We also assume to have a user called **web** which handles the Django
application.

Bootstrap
=========

As **root**, install virtualenv::

  # apt-get install python-virtualenv python-pip

We also need the versioning tools::

  # apt-get install git mercurial subversion


Web servers
===========

Apache
------

We run *Django* using Apache2/WSGI::

   # apt-get install apache2-mpm-prefork libapache2-mod-wsgi

Ngnix
-----

Static files are handled by Nginx::

   # apt-get install nginx


Setting-up the app
==================

As **web**::

	web@i4p-prod:~$ mkdir virtualenvs
	web@i4p-prod:~$ cd virtualenvs/
	web@i4p-prod:~/virtualenvs$ virtualenv --no-site-packages imaginationforpeople.org

then clone the app::

	web@i4p-prod:~/virtualenvs$ cd imaginationforpeople.org/
	web@i4p-prod:~/virtualenvs/imaginationforpeople.org$ git clone ssh://webapp@code.imaginationforpeople.com/var/repositories/imaginationforpeople.git
	

