#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import with_statement

import os.path
from fabric.api import *

def commonenv():
    "Base environment"
    env.venvname = "imaginationforpeople.com"
    env.projectname = "i4p_project"
    env.gitrepo = "ssh://webapp@code.imaginationforpeople.com/var/repositories/imaginationforpeople.git"

def reloadapp():
    "Touch the wsgi"


def venvcmd(cmd, shell=True, user="webapp", pty=True):
    with cd(env.venvfullpath + '/' + env.projectname):
        sudo('source %(venvfullpath)s/bin/activate && ' % env + cmd, shell=shell, user=user,pty=pty)

    
def tests():
    "Run all tests on remote"
    venvcmd('./manage.py test')

def syncdb():
    venvcmd('./manage.py syncdb --noinput')
    venvcmd('./manage.py migrate')

def prodenv():
    "production environment - NOT IMPLEMENTED YET"
    fail("Not implemented yet")
    pass
    
def stagenv():
    "Stagging environment"
    commonenv()
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['pmironov@dev.imaginationforpeople.com']
    env.gitrepo = "/var/repositories/imaginationforpeople.git"
    env.venvbasepath = "/home/webapp/virtualenvs"
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'

def build_env():
    "Build the virtualenv"
    require('venvfullpath', provided_by=('devenv', 'prodenv'))
    sudo('rm /tmp/distribute*') # clean after hudson
    cmd = 'virtualenv --no-site-packages --distribute %(venvfullpath)s' % env
    sudo(cmd, user="webapp")
    sudo('rm /tmp/distribute*') # clean after myself

def update_requirements():
    "update external dependencies on remote host"
    cmd = "pip install -E %(venvfullpath)s -Ur %(venvfullpath)s/%(projectname)s/requirements.txt" % env
    sudo(cmd, user="webapp")

def deploy_bootstrap():
    "Deploy the project the first time."
    build_env()
    clonegitcmd = "git clone %(gitrepo)s %(projectname)s" % env
    with cd(env.venvfullpath):
        sudo(clonegitcmd, user="webapp")
    update_requirements()
    syncdb()
    tests()
    
def update():
    "Update the project"
    with cd(env.venvfullpath + '/%(projectname)s/' % env):
        sudo('git pull', user="webapp")
    update_requirements()
    syncdb()
    tests()
    
def reload_webserver():
    """
    Reload the webserver stack.
    """
    sudo('apache2ctl -k graceful')
    
def configure_webserver():
    """
    Configure the webserver stack.
    """
    fullprojectpath = env.venvfullpath + '/%(projectname)s/' % env
    sudo('cp %sapache/dev.imaginationforpeople.com /etc/apache2/sites-avaible/dev.imaginationforpeople.com' % fullprojectpath)
    reload_webserver()
    
def install_webserver():
    """
    Will install the webserver stack (only apache for the moment. Could use varnish and nginx later on .. maybe)
    """
    sudo('apt-get install apache2-mpm-prefork libapache2-mod-wsgi -y')
    
    
def install_buildeps():
    """
    Will install commonly needed build deps for pip django virtualenvs.
    """
    sudo('apt-get install -y build-essential python-dev libjpeg62-dev libpng-dev zlib1g-dev libfreetype6-dev liblcms-dev libpq-dev')


def meta_full_bootstrap()
    """
    For use on new, empty environnements
    """
    install_webserver()
    install_buildeps()
    deploy_bootstrap()
    reload_webserver()

    
    
    
    
    
    
