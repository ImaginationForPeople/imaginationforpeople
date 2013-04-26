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


.. _database-server-configuration:

Database server configuration
*****************************

==========
Postgresql
==========

Access control
==============

From the file :file:`/etc/postgresql/8.4/main/pg_hba.conf`, update the
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



Forum setup
***********

Askbot (forum next-gen) is installed by default. 

Two background jobs are required:

* the email sender daemon that is a cron job. The script to schedule is *cron/askbot-cron* :
* and the celery daemon that can be launched with ``./manage.py celeryd --purge``
    
Installing SolR search engine
*****************************

SolR is the search engine used in production environement (while Whoos backend is the default option in dev environment).
Be sure that java is installed on your server before starting. Official Download Location: http://www.apache.org/dyn/closer.cgi/lucene/solr/
Then choose a mirror and copy the link for a 3.* version. Create a solr dir in your virtual-env: 
	web@i4p-prod:~/virtualenvs$ mkdir solr   
	web@i4p-prod:~/virtualenvs$ cd solr    
	web@i4p-prod:~/virtualenvs/solr$ wget http://apache.mirrors.hoobly.com/lucene/solr/3.6.2/apache-solr-3.6.2.tgz   
	web@i4p-prod:~/virtualenvs/solr$ tar xvzf apache-solr-3.6.2.tgz    
	web@i4p-prod:~/virtualenvs/solr$ cd apache-solr-3.5.0    
	web@i4p-prod:~/virtualenvs/solr/apache-solr-3.6.2$ cd example    
	web@i4p-prod:~/virtualenvs/solr/apache-solr-3.6.2/example$ java -jar start.jar    

You’ll need to revise your schema. You can generate this from your application (once Haystack is installed and setup)
by running 
	./manage.py build_solr_schema > schema.xml 
Take the output from that command and place it in apache-solr-3.5.0/example/solr/conf/schema.xml. Then restart Solr. 

KNOWN BUG: With the current setting (Haystack 2.* + SolR 3.6), SolR will normally complain it does not find stopword file
(stopwords_en.txt e.g) in solr conf dir. This path is written in schema.xml. You should then either copy the 
named file from conf/lang in /conf or change the path in schema.xml
