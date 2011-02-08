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


def venvcmd(cmd, shell=True, pty=True):
    with cd(env.venvfullpath + '/' + env.projectname):
        run('source %(venvfullpath)s/bin/activate && ' % env + cmd, shell, pty)

    
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
    env.hosts = ['webapp@dev.imaginationforpeople.com']
    env.gitrepo = "/var/repositories/imaginationforpeople.git"
    env.venvbasepath = "/home/webapp/virtualenvs"
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'

def build_env():
    "Build the virtualenv"
    require('venvfullpath', provided_by=('devenv', 'prodenv'))
    cmd = 'virtualenv --no-site-packages --distribute %(venvfullpath)s' % env
    run(cmd)
    run('rm /tmp/distribute*')

def update_requirements():
    "update external dependencies on remote host"
    cmd = "pip install -E %(venvfullpath)s -Ur %(venvfullpath)s/%(projectname)s/requirements.txt" % env
    run(cmd)

def deploy_bootstrap():
    "Deploy the project the first time."
    build_env()
    clonegitcmd = "git clone %(gitrepo)s %(projectname)s" % env
    with cd(env.venvfullpath):
        run(clonegitcmd)
    update_requirements()
    syncdb()
    tests()
    
def update():
    "Update the project"
    with cd(env.venvfullpath + '/%(projectname)s/' % env):
        run('git pull')
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
    sudo('')
    
def install_webserver():
    """
    Will install the webserver stack (only apache for the moment. Could use varnish and nginx later on .. maybe)
    """
    sudo('apt-get install apache2-mpm-prefork libapache2-mod-wsgi')
    
    
    
    
    
    
    
    
