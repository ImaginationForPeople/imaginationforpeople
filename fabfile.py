#!/bin/env python
# -*- coding:utf-8 -*-
from __future__ import with_statement

import os.path
from fabric.api import *
from fabric.contrib.files import *

def commonenv():
    "Base environment"
    env.venvname = "imaginationforpeople.com"
    env.projectname = "imaginationforpeople"
    env.gitrepo = "ssh://webapp@code.imaginationforpeople.com/var/repositories/imaginationforpeople.git"

def reloadapp():
    "Touch the wsgi"
    venvcmd('touch apache/%(wsginame)s' % env)


def venvcmd(cmd, shell=True, user="webapp", pty=False, subdir=""):
    with cd(env.venvfullpath + '/' + env.projectname + '/' + subdir):
        return sudo('source %(venvfullpath)s/bin/activate && ' % env + cmd, shell=shell, user=user,pty=pty)
    
def tests():
    "Run all tests on remote"
    venvcmd('./manage.py test')
    venvcmd('./manage.py harvest --verbosity=2')

def syncdb():
    venvcmd('./manage.py syncdb --noinput')
    venvcmd('./manage.py migrate')

def prodenv():
    "production environment - Will need some work when moving to seperate server"
    commonenv()
    env.venvname = "prod.imaginationforpeople.com"
    env.wsginame = "prod.wsgi"
    env.urlhost = "www.imaginationforpeople.com"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['prod.imaginationforpeople.com']
    env.gitrepo = "/var/repositories/imaginationforpeople.git"
    env.venvbasepath = "/home/webapp/virtualenvs"
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'
    
    
def stagenv():
    "Stagging environment"
    commonenv()
    env.wsginame = "staging.wsgi"
    env.urlhost = "dev.imaginationforpeople.com"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['dev.imaginationforpeople.com']
    env.gitrepo = "/var/repositories/imaginationforpeople.git"
    env.venvbasepath = "/home/webapp/virtualenvs"
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'

def build_env():
    "Build the virtualenv"
    require('venvfullpath', provided_by=('devenv', 'prodenv'))
    sudo('rm /tmp/distribute* || echo "ok"') # clean after hudson
    cmd = 'virtualenv --no-site-packages --distribute %(venvfullpath)s' % env
    sudo(cmd, user="webapp")
    sudo('rm /tmp/distribute* || echo "ok"') # clean after myself
    

def update_requirements():
    "update external dependencies on remote host"
    cmd = "pip install -E %(venvfullpath)s -Ur %(venvfullpath)s/%(projectname)s/requirements.txt" % env
    sudo(cmd, user="webapp")

def fixperms():
    """
    fix permissions
    """
    with cd(env.venvfullpath):
        sudo('chown :www-data -R %(projectname)s && chmod g+rw -R %(projectname)s' % env)

def compile_messages():
    """
    Run compile messages and reload the app
    """
    apps = venvcmd('ls -d */', subdir="apps").split("\n")
    cmd = "django-admin.py compilemessages"
    print apps
    for app in apps :
        appsubdir = 'apps/%s' % app
        cwd = venvcmd('pwd', subdir=appsubdir)
        if exists(cwd + '/locale') :
            venvcmd(cmd, subdir=appsubdir)
    fixperms()
    reloadapp()

def deploy_bootstrap():
    "Deploy the project the first time."
    build_env()
    clonegitcmd = "git clone %(gitrepo)s %(projectname)s" % env
    fixperms()
    update_requirements()
    syncdb()
    tests()


def _updatemaincode():
    """
    Private : we don't want people updateing code without running tests
    """
    with cd(env.venvfullpath + '/%(projectname)s/' % env):
        sudo('git pull', user="webapp")
    
def fullupdate():
    """
    Full Update the maincode and the deps
    """
    _updatemaincode()
    update_requirements()
    syncdb()
    tests()
    reloadapp()

def update():
    "Fast Update : project maincode"
    _updatemaincode()
    syncdb()
    tests()
    reloadapp()
    
def reload_webserver():
    """
    Reload the webserver stack.
    """
    sudo('apache2ctl -k graceful')
    
def check_or_install_logdir():
    """
    Make sure the log directory exists and has right mode and ownership
    """
    with cd(env.venvfullpath + '/'):
        sudo('mkdir -p logs/ ; chown www-data logs; chmod o+rwx logs ; pwd')

def configure_webserver():
    """
    Configure the webserver stack.
    """
    fullprojectpath = env.venvfullpath + '/%(projectname)s/' % env
    sudo('cp %sapache/%s /etc/apache2/sites-available/%s' % (fullprojectpath, env.urlhost, env.urlhost))
    sudo('a2ensite %s' % env.urlhost)
    check_or_install_logdir()
    reload_webserver()
    
def install_webserver():
    """
    Will install the webserver stack (only apache for the moment. Could use varnish and nginx later on .. maybe)
    """
    sudo('apt-get install apache2-mpm-itk libapache2-mod-wsgi -y')
    
    
def install_buildeps():
    """
    Will install commonly needed build deps for pip django virtualenvs.
    """
    sudo('apt-get install -y build-essential python-dev libjpeg62-dev libpng-dev zlib1g-dev libfreetype6-dev liblcms-dev libpq-dev')


def meta_full_bootstrap():
    """
    For use on new, empty environnements
    """
    install_webserver()
    install_buildeps()
    deploy_bootstrap()
    configure_webserver()
    reload_webserver()

    
    
    
    
    
    
