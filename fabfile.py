#!/bin/env python
# -*- coding:utf-8 -*-
from __future__ import with_statement

import os.path
import time

import fabric.operations
from fabric.operations import put, get
from fabric.api import *
from fabric.colors import cyan
from fabric.contrib.files import *

@task
def reloadapp():
    """
    Touch the wsgi
    """
    print(cyan('Reloading all wsgi applications in : %s' % env.venvfullpath + '/' + env.projectname))
    #this may accidentally reload staging environments and the like, but it's the only reliable way to 
    #hit any multisites defined. 
    with cd(env.venvfullpath + '/' + env.projectname):
        run('touch apache/*')

def venvcmd(cmd, shell=True, user=None, pty=False, subdir=""):
    if not user:
        user = env.user

    with cd(env.venvfullpath + '/' + env.projectname + '/' + subdir):
        return run('source %(venvfullpath)s/bin/activate && ' % env + cmd, shell=shell, pty=pty)

def venv_prefix():
    return 'source %(venvfullpath)s/bin/activate' % env

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

    env.db_user = 'imaginationforpeople'
    env.db_name = 'imaginationforpeople'
    env.dbdumps_dir = os.path.join(tempfile.gettempdir(), '%s_dumps' % env.projectname)
    
    env.gitrepo = "ssh://webapp@i4p-dev.imaginationforpeople.org/var/repositories/imaginationforpeople.git"
    env.gitbranch = "master"


@task
def prodenv():
    """
    [ENVIRONMENT] Production
    """
    commonenv()
    env.venvname = "imaginationforpeople.org"
    env.wsginame = "prod.wsgi"
    env.urlhost = "www.imaginationforpeople.org"
    env.user = "web"
    env.home = "www"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['i4p-prod.imaginationforpeople.org']

    env.gitbranch = "master"

    env.venvbasepath = os.path.join("/home", env.home, "virtualenvs")
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'
    
@task    
def stagenv():
    """
    [ENVIRONMENT] Staging
    """
    commonenv()
    env.wsginame = "staging.wsgi"
    env.urlhost = "staging.imaginationforpeople.org"
    env.user = "webapp"
    env.home = "webapp"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['i4p-dev.imaginationforpeople.org']
    
    env.gitrepo = "git://github.com/ImaginationForPeople/imaginationforpeople.git"
    env.gitbranch = "feature/project-support"

    env.venvbasepath = os.path.join("/home", env.home, "virtualenvs")
    env.venvfullpath = env.venvbasepath + '/' + env.venvname + '/'


@task
def devenv():
    """
    [ENVIRONMENT] Developpement (must be run from the project path: 
    the one where the fabfile is)
    """
    commonenv()
    env.wsginame = "dev.wsgi"
    env.urlhost = "localhost"
    #env.user = "webapp"
    #env.home = "webapp"
    require('venvname', provided_by=('commonenv',))
    env.hosts = ['localhost']

    current_path = local('pwd',capture=True)
    
    env.gitrepo = "git://github.com/ImaginationForPeople/imaginationforpeople.git"
    env.gitbranch = "develop"

    env.venvbasepath = os.path.normpath(os.path.join(current_path,"../../"))
    env.venvfullpath = os.path.normpath(os.path.join(current_path,"../"))

## Virtualenv
def build_virtualenv():
    """
    Build the virtualenv
    """
    print(cyan('Creating a fresh virtualenv'))
    require('venvfullpath', provided_by=('stagenv', 'prodenv'))
    sudo('rm /tmp/distribute* || echo "ok"') # clean after hudson
    run('virtualenv --no-site-packages --distribute %(venvfullpath)s' % env)
    sudo('rm /tmp/distribute* || echo "ok"') # clean after myself
    

@task
def update_requirements(force=False):
    """
    update external dependencies on remote host
    """
    print(cyan('Updating requirements using PIP'))
    run('%(venvfullpath)s/bin/pip install -U pip' % env)
    
    if force:
        cmd = "%(venvfullpath)s/bin/pip install -I -r %(venvfullpath)s/%(projectname)s/requirements.txt" % env
    else:
        cmd = "%(venvfullpath)s/bin/pip install -r %(venvfullpath)s/%(projectname)s/requirements.txt" % env
    run("yes w | %s" % cmd)


## Django
def app_db_update():
    """
    Migrates database using south
    """
    print(cyan('Migrating Django database'))
    venvcmd('./manage.py syncdb --noinput')
    venvcmd('./manage.py migrate')

def app_db_install():
    """
    Install db the first time and fake migrations
    """
    print(cyan('Installing Django database'))
    venvcmd('./manage.py syncdb --all --noinput')
    venvcmd('./manage.py migrate --fake')


def collect_static_files():
    """
    Collect static files such as pictures
    """
    print(cyan('Collecting static files'))
    venvcmd('./manage.py collectstatic --noinput')
    
    #Workaround for collectstatic bug on prod server
    with cd(env.venvfullpath + '/' + env.projectname + '/static'):
        run('cp -Rp compiled_sass/* css/')

@task
def make_messages():
    """
    Run *.po file generation for translation
    """
    appspath=env.venvfullpath + '/' + env.projectname + '/' + "apps"
    with cd(appspath):
        apps = run('ls -d */').split(None)
    cmd = "django-admin.py makemessages -a -e html,txt"
    print(cyan('Generating .po files for the following apps: %s' % apps))
    for app in apps:
        appsubdir = 'apps/%s' % app
        if exists(appspath + '/' + app + '/' + '/locale'):
            print(cyan('\t * %s' % appsubdir))
            venvcmd(cmd, subdir=appsubdir)

@task
def compile_messages():
    """
    Run compile *.mo file from *.po
    """
    appspath=env.venvfullpath + '/' + env.projectname + '/' + "apps"
    with cd(appspath):
        apps = run('ls -d */').split(None)
    cmd = "django-admin.py compilemessages -v0"
    print(cyan('Compiling i18 messages for the following apps: %s' % apps))
    for app in apps:
        appsubdir = 'apps/%s' % app
        if exists(appspath + '/' + app + '/' + '/locale'):
            print(cyan('\t * %s' % appsubdir))
            venvcmd(cmd, subdir=appsubdir)

@task
def compile_stylesheets():
    """
    Generate *.css files from *.scss
    """
    with cd(env.venvfullpath + '/' + env.projectname + '/static'):
        run('rm -rf compiled_sass')
        run('bundle exec compass compile --force', shell=True)
            
def tests():
    """
    Run all tests on remote
    """
    print(cyan('Running TDD tests'))
    venvcmd('./manage.py test')

    print(cyan('Running BDD tests'))
    venvcmd('./manage.py harvest --verbosity=2')

def fixperms():
    # Fix perms
    with cd(env.venvfullpath):
        with cd("%(projectname)s" % env):
            run('mkdir media/uploads media/cache static/CACHE media/mugshots -p')
            sudo('chown www-data -R media/uploads media/cache media/mugshots static/CACHE')
    
@task
def bootstrap_venv():
    """
    Create the virtualenv and install the app
    """
    execute(build_virtualenv)
    execute(app_install)
    execute(fixperms)

def clone_repository():
    """
    Clone repository and remove the exsiting one if necessary
    """
    print(cyan('Cloning Git repository'))

    with cd(env.venvfullpath):
        # Remove dir if necessary
        if exists("%(projectname)s" % env):
            sudo("rm -rf %(projectname)s" % env)

        # Clone
        run("git clone --branch {0} {1} {2}".format(env.gitbranch,
                                                    env.gitrepo,
                                                    env.projectname)
        )
    
            
def updatemaincode():
    """
    Update code and/or switch branch
    """
    print(cyan('Updating Git repository'))
    with cd(os.path.join(env.venvfullpath, '%(projectname)s' % env)):
        run('git fetch')
        run('git checkout %s' % env.gitbranch)
        run('git pull origin %s' % env.gitbranch)

@task
def app_install():
    """
    (Re)install app to target server
    """
    execute(clone_repository)
    execute(update_requirements, force=True)
    execute(compile_messages)
    execute(app_db_install)
    execute(collect_static_files)
    # tests()
    execute(reloadapp)
    
@task
def app_fullupdate():
    """
    Full Update: maincode and dependencies
    """
    execute(updatemaincode)
    execute(compile_messages)
    execute(update_compass)
    execute(compile_stylesheets)
    execute(update_requirements, force=False)
    execute(app_db_update)
    execute(collect_static_files)
    # tests()
    execute(reloadapp)
    execute(webservers_reload)

@task
def app_update():
    """
    Fast Update: don't update requirements
    """
    execute(updatemaincode)
    execute(compile_messages)
    execute(compile_stylesheets)
    execute(app_db_update)
    execute(collect_static_files)
    # tests()
    execute(reloadapp)
    execute(webservers_reload)

## Webserver
def configure_webservers():
    """
    Configure the webserver stack.
    """
    # apache
    print(cyan('Configuring Apache'))
    fullprojectpath = env.venvfullpath + '/%(projectname)s/' % env
    sudo('cp %sapache/%s /etc/apache2/sites-available/%s' % (fullprojectpath, env.urlhost, env.urlhost))
    sudo('a2ensite %s' % env.urlhost)

    # nginx
    print(cyan('Configuring Nginx'))
    sudo('cp %snginx/%s /etc/nginx/sites-available/%s' % (fullprojectpath, env.urlhost, env.urlhost))
    with cd('/etc/nginx/sites-enabled/'):
        sudo('ln -sf ../sites-available/%s .' % env.urlhost)

    # Fix log dir
    execute(check_or_install_logdir)

    
def install_webservers():
    """
    Install the webserver stack
    """
    print(cyan('Installing web servers'))
    sudo('apt-get install apache2-mpm-prefork libapache2-mod-wsgi -y')
    sudo('apt-get install nginx -y')

@task
def webservers_reload():
    """
    Reload the webserver stack.
    """
    print(cyan("Reloading apache"))
    # Apache (sudo is part of command line here because we don't have full
    # sudo access
    run('sudo /etc/init.d/apache2 reload')

    # Nginx (sudo is part of command line here because we don't have full
    # sudo access
    print(cyan("Reloading nginx"))
    run('sudo /etc/init.d/nginx reload')

def webservers_stop():
    """
    Stop all webservers
    """
    # Apache
    sudo('/etc/init.d/apache2 stop')

    # Nginx
    sudo('/etc/init.d/nginx stop')    

def webservers_start():
    """
    Start all webservers
    """
    # Apache
    sudo('/etc/init.d/apache2 start')

    # Nginx
    sudo('/etc/init.d/nginx start')

    
def check_or_install_logdir():
    """
    Make sure the log directory exists and has right mode and ownership
    """
    print(cyan('Installing a log dir'))
    with cd(env.venvfullpath + '/'):
        sudo('mkdir -p logs/ ; chown www-data logs; chmod o+rwx logs ; pwd')


## Database server
def install_database_server():
    """
    Install a postgresql DB
    """
    print(cyan('Installing Postgresql'))
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
    print(cyan('Installing base tools'))
    sudo('apt-get install -y python-virtualenv python-pip')
    sudo('apt-get install -y git mercurial subversion')
    sudo('apt-get install -y gettext')

def install_builddeps():
    """
    Will install commonly needed build deps for pip django virtualenvs.
    """
    print(cyan('Installing compilers and required libraries'))
    sudo('apt-get install -y build-essential python-dev libjpeg62-dev libpng12-dev zlib1g-dev libfreetype6-dev liblcms-dev libpq-dev libxslt1-dev libxml2-dev')

@task
def install_rbenv():
    # Install rbenv:
    sudo('git clone git://github.com/sstephenson/rbenv.git ~/.rbenv', user=env.user)
    # Add rbenv to the path:
    sudo('echo \'export PATH="$HOME/.rbenv/bin:$PATH"\' >> .bash_profile', user=env.user)
    sudo('echo \'eval "$(rbenv init -)"\' >> .bash_profile', user=env.user)
    sudo('source ~/.bash_profile', user=env.user)
    # Install ruby-build:
    with cd('/tmp'):
        sudo('git clone git://github.com/sstephenson/ruby-build.git', user=env.user)
    with cd('/tmp/ruby-build'):
        sudo('./install.sh')
    # Install Ruby 1.9.3-p125:
    sudo('rbenv install 1.9.3-p125', user=env.user)
    sudo('rbenv global 1.9.3-p125', user=env.user)
    # Rehash:
    sudo('rbenv rehash', user=env.user)
    
    #install bundler
    sudo('gem install bundler', user=env.user)
    sudo('rbenv rehash')

@task
def install_compass():
    with cd(env.venvfullpath + '/' + env.projectname + '/'):
        run('rm -rf vendor/bundle')
        execute(update_compass)
@task
def update_compass():
    with cd(env.venvfullpath + '/' + env.projectname + '/'):
        run('bundle install --path=vendor/bundle')

@task
def bootstrap_full():
    """
    Install system tools, create venv and install app
    """
    sudo('apt-get update')
    
    execute(install_basetools)
    execute(install_database_server)
    execute(install_webservers)
    execute(install_builddeps)
    execute(install_rbenv)
    execute(install_compass)
    
    execute(deploy_bootstrap)
    
    if(env.wsginame == 'dev.wsgi'):
        execute(install_devdeps);

    execute(configure_webservers)
    execute(webservers_reload)


@task
def mirror_prod_media():
    """
    Mirror the production media (pictures, ...) the target server
    """
    assert(env.wsginame in ('staging.wsgi',))

    # Files
    with cd(os.path.join(env.venvfullpath, env.projectname)):
        sudo('rm -rf media')
        run('scp -r web@i4p-prod.imaginationforpeople.org:/home/www/virtualenvs/imaginationforpeople.org/imaginationforpeople/media/ .')

        sudo('chown www-data -R media')
        sudo('chmod u+rw -R media')

@task
def database_dump():
    """
    Dumps the database on remote site
    """
    if not exists(env.dbdumps_dir):
        run('mkdir -m700 %s' % env.dbdumps_dir)

    filename = 'db_%s.sql' % time.strftime('%Y%m%d')
    compressed_filename = '%s.bz2' % filename
    absolute_path = os.path.join(env.dbdumps_dir, compressed_filename)

    # Dump
    with prefix(venv_prefix()), cd(os.path.join(env.venvfullpath, env.projectname)):
        run('grep "DATABASE" -A 8 site_settings.py')
        run('pg_dump -U%s %s | bzip2 -9 > %s' % (env.db_user,
                                                 env.db_name,
                                                 absolute_path)
            )

    # Make symlink to latest
    with cd(env.dbdumps_dir):
        run('ln -sf %s current_database.sql.bz2' % compressed_filename)


@task
def database_download():
    """
    Dumps and downloads the database from the target server
    """
    execute(database_dump)
    get(os.path.join(env.dbdumps_dir, 'current_database.sql.bz2'), 'current_database.sql.bz2')

@task    
def database_restore():
    """
    Restores the database to the remote server
    """
    assert(env.wsginame in ('staging.wsgi', 'dev.wsgi'))

    if(env.wsginame == 'dev.wsgi'):
        remote_db_path = os.path.join(env.venvfullpath, env.projectname, 'current_database.sql.bz2')
    else:
        remote_db_path = os.path.join(env.venvfullpath, 'current_database.sql.bz2')

    if(env.wsginame != 'dev.wsgi'):
        put('current_database.sql.bz2', remote_db_path)

    if(env.wsginame != 'dev.wsgi'):
        execute(webservers_stop)
    
    # Drop db
    with settings(warn_only=True):
        sudo('su - postgres -c "dropdb imaginationforpeople"')

    # Create db
    sudo('su - postgres -c "createdb -E UNICODE -Ttemplate0 -O%s %s"' % (env.db_user, env.db_name))
    run('pwd')
    # Restore data
    with prefix(venv_prefix()), cd(os.path.join(env.venvfullpath, env.projectname)):
        run('grep "DATABASE" -A 8 site_settings.py')
        run('bunzip2 -c %s | psql -U%s %s' % (remote_db_path,
                                              env.db_user,
                                              env.db_name)
        )

    if(env.wsginame != 'dev.wsgi'):
        execute(webservers_start)
