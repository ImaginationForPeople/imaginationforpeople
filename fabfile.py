#!/bin/env python
# -*- coding:utf-8 -*-
from __future__ import with_statement

import os.path
from fabric.api import *
from fabric.colors import cyan
from fabric.contrib.files import *


def reloadapp():
    """
    Touch the wsgi
    """
    venvcmd('touch apache/%(wsginame)s' % env)


def venvcmd(cmd, shell=True, user=None, pty=False, subdir=""):
    if not user:
        user = env.user

    with cd(env.venvfullpath + '/' + env.projectname + '/' + subdir):
        return sudo('source %(venvfullpath)s/bin/activate && ' % env + cmd, shell=shell, user=user, pty=pty)
    

def printenv():
    """
    Print shell env
    """
    venvcmd('env')

## Server scenarios
def commonenv():
    """
    Base environment
    """
    env.venvname = "imaginationforpeople.org"
    env.projectname = "imaginationforpeople"
    env.gitrepo = "ssh://webapp@code.imaginationforpeople.com/var/repositories/imaginationforpeople.git"
    env.gitbranch = "master"


def prodenv():
    """
    production environment - Will need some work when moving to seperate server
    """
    commonenv()
    env.venvname = "imaginationforpeople.org"
    env.wsginame = "prod.wsgi"
    env.urlhost = "www.imaginationforpeople.org"
    env.user = "web"
    env.home = "www"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['i4p-prod.imaginationforpeople.org']

    env.gitrepo = "ssh://webapp@code.imaginationforpeople.com/var/repositories/imaginationforpeople.git"
    env.gitbranch = "iteration7"

    env.venvbasepath = os.path.join("/home", env.home, "virtualenvs")
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'
    
    
def stagenv():
    """
    Stagging environment
    """
    commonenv()
    env.wsginame = "staging.wsgi"
    env.urlhost = "dev.imaginationforpeople.com"
    env.user = "webapp"
    env.home = "webapp"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['dev.imaginationforpeople.com']

    env.gitrepo = "/var/repositories/imaginationforpeople.git"
    env.gitbranch = "iteration7"

    env.venvbasepath = os.path.join("/home", env.home, "virtualenvs")
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'


## Virtualenv
def build_virtualenv():
    """
    Build the virtualenv
    """
    require('venvfullpath', provided_by=('devenv', 'prodenv'))
    sudo('rm /tmp/distribute* || echo "ok"') # clean after hudson
    cmd = 'virtualenv --no-site-packages --distribute %(venvfullpath)s' % env
    sudo(cmd, user=env.user)
    sudo('rm /tmp/distribute* || echo "ok"') # clean after myself
    

def update_requirements():
    """
    update external dependencies on remote host
    """
    cmd = "pip install -E %(venvfullpath)s -Ur %(venvfullpath)s/%(projectname)s/requirements.txt" % env
    sudo(cmd, user=env.user)

def fixperms():
    """
    fix permissions
    """
    with cd(env.venvfullpath):
        # sudo('chown :www-data -R %(projectname)s && chmod g+rw -R %(projectname)s' % env)
        # FIXME: This SUCKS
        pass

## Django
def syncdb():
    venvcmd('./manage.py syncdb --noinput')
    venvcmd('./manage.py migrate')


def collect_static_files():
    """
    Collect static files such as pictures
    """
    venvcmd('./manage.py collectstatic --noinput')

def compile_messages():
    """
    Run compile messages and reload the app
    """
    apps = venvcmd('ls -d */', subdir="apps").split("\n")
    cmd = "django-admin.py compilemessages -v0"
    print "Need to compile i18n messages for the following apps:", apps
    for app in apps:
        appsubdir = 'apps/%s' % app
        cwd = venvcmd('pwd', subdir=appsubdir)
        if exists(cwd + '/locale'):
            print cmd, 'in', appsubdir
            venvcmd(cmd, subdir=appsubdir)
    fixperms()
    reloadapp()

def tests():
    """
    Run all tests on remote
    """
    venvcmd('./manage.py test')
    venvcmd('./manage.py harvest --verbosity=2')


def deploy_bootstrap():
    """
    Deploy the project the first time.
    """
    build_virtualenv()

    with cd(env.venvfullpath):
        run("git clone %(gitrepo)s %(projectname)s" % env)
        run("git fetch origin %s" % env.gitbranch)

    fullupdate()

def _updatemaincode():
    """
    Private : we don't want people updating the code without running
    tests
    """
    with cd(env.venvfullpath + '/%(projectname)s/' % env):
        run('git checkout %s' % env.gitbranch)
        sudo('git pull origin %s' % env.gitbranch, user=env.user)
    
def fullupdate():
    """
    Full Update the maincode and the deps
    """
    _updatemaincode()
    update_requirements()
    compile_messages()
    syncdb()
    collect_static_files()
    # tests()
    reloadapp()

def update():
    """
    Fast Update : project maincode
    """
    _updatemaincode()
    compile_messages()
    syncdb()
    collect_static_files()
    # tests()
    reloadapp()

## Webserver
def configure_webservers():
    """
    Configure the webserver stack.
    """
    # apache
    fullprojectpath = env.venvfullpath + '/%(projectname)s/' % env
    sudo('cp %sapache/%s /etc/apache2/sites-available/%s' % (fullprojectpath, env.urlhost, env.urlhost))
    sudo('a2ensite %s' % env.urlhost)

    # nginx
    with cd('/etc/nginx/sites-enabled/'):
        sudo('ln -s ../sites-available/%s .' % env.urlhost)
        
    sudo('cp %snginx/%s /etc/nginx/sites-available/%s' % (fullprojectpath, env.urlhost, env.urlhost))

    # Fix log dir
    check_or_install_logdir()

    
def install_webservers():
    """
    Install the webserver stack
    """
    sudo('apt-get install apache2-mpm-prefork libapache2-mod-wsgi -y')
    sudo('apt-get install nginx -y')

def reload_webservers():
    """
    Reload the webserver stack.
    """
    print(cyan("reloading apache"))
    # Apache
    sudo('apache2ctl -k graceful')

    # Nginx
    print(cyan("reloading nginx"))
    sudo('/etc/init.d/nginx restart')
    
def check_or_install_logdir():
    """
    Make sure the log directory exists and has right mode and ownership
    """
    with cd(env.venvfullpath + '/'):
        sudo('mkdir -p logs/ ; chown www-data logs; chmod o+rwx logs ; pwd')


## Database server
def install_database_server():
    """
    Install a postgresql DB
    """
    sudo('apt-get install -y postgresql-8.4 postgresql-8.4')

def setup_database():
    """
    Create a user and a DB for the project
    """
    # FIXME: pg_hba has to be changed by hand (see doc)
    # FIXME: Password has to be set by hand (see doc)
    sudo('createuser %s -D -R -S' % env.projectname, user='postgres')
    sudo('createdb -O%s %s' % (env.projectname, env.projectname), user='postgres')
    
## Server packages    
def install_basetools():
    """
    Install required base tools
    """
    sudo('apt-get install -y python-virtualenv python-pip')
    sudo('apt-get install -y git mercurial subversion')
    sudo('apt-get install -y gettext')

def install_builddeps():
    """
    Will install commonly needed build deps for pip django virtualenvs.
    """
    sudo('apt-get install -y build-essential python-dev libjpeg62-dev libpng-dev zlib1g-dev libfreetype6-dev liblcms-dev libpq-dev libxslt1-dev libxml2-dev')



def meta_full_bootstrap():
    """
    For use on new, empty environnements
    """
    install_basetools()
    install_database_server()
    install_webservers()
    install_builddeps()

    deploy_bootstrap()

    configure_webservers()
    reload_webservers()

    
    
    
    
    
    
