#!/bin/env python
# -*- coding:utf-8 -*-
from __future__ import with_statement

from os import getenv
import os.path
import time
import pipes

import fabric.operations
from fabric.operations import put, get, env
from fabric.api import *
from fabric.colors import cyan
from fabric.contrib.files import *
from os.path import expanduser
@task
def reloadapp():
    """
    Touch the wsgi
    """
    print(cyan('Reloading all wsgi applications in : %s' % env.projectpath))
    #this may accidentally reload staging environments and the like, but it's the only reliable way to 
    #hit any multisites defined. 
    with cd(env.projectpath):
        run('touch apache/*')
    if(env.wsginame == 'prod.wsgi'):
        flushmemcache()

@task
def flushmemcache():
    """
    Resetting all data in memcached
    """
    print(cyan('Resetting all data in memcached :'))
    run('echo "flush_all" | /bin/netcat -q 2 127.0.0.1 11211')


def venvcmd(cmd, shell=True, user=None, pty=False, subdir=""):
    if not user:
        user = env.user

    with cd(os.path.join(env.projectpath,subdir)):
        return run('source %(venvpath)s/bin/activate && ' % env + cmd, shell=shell, pty=pty)

def venv_prefix():
    return 'source %(venvpath)s/bin/activate' % env

def remote_db_path():
    return os.path.join(env.projectpath, 'current_database.sql.bz2')

def printenv():
    """
    Print shell env
    """
    venvcmd('env')

## Server scenarios
def commonenv(projectpath, venvpath=None):
    """
    Base environment
    """
    env.projectpath = projectpath
    if venvpath:
        env.venvpath = venvpath
    else: 
        env.venvpath = os.path.join(projectpath,"venv")
    env.projectname = 'imaginationforpeople'
    env.db_user = 'imaginationforpeople'
    env.db_name = 'imaginationforpeople'
    env.dbdumps_dir = os.path.join(tempfile.gettempdir(), '%s_dumps' % env.projectname)
    
    #env.gitrepo = "ssh://webapp@i4p-dev.imaginationforpeople.org/var/repositories/imaginationforpeople.git"
    env.gitrepo = "git://github.com/ImaginationForPeople/imaginationforpeople.git"
    env.gitbranch = "master"
    
    #Used to compute paths
    env.postgis_version  = "1.5"


@task
def prodenv():
    """
    [ENVIRONMENT] Production
    """
    env.user = "web"
    env.home = "www"
    venvname = "imaginationforpeople.org"
    venvpath = os.path.join("/home", env.home, "virtualenvs", venvname)
    projectpath = venvpath + '/' + 'imaginationforpeople' + '/'
    commonenv(projectpath, venvpath)
    env.wsginame = "prod.wsgi"
    env.urlhost = "www.imaginationforpeople.org"

    require('venvpath', provided_by=('commonenv',))
    env.hosts = ['i4p-prod.imaginationforpeople.org']

    env.gitbranch = "master"


    
@task    
def stagenv():
    """
    [ENVIRONMENT] Staging
    """
    env.user = "webapp"
    env.home = "webapp"
    venvname = "imaginationforpeople.org"
    venvpath = os.path.join("/home", env.home, "virtualenvs", venvname)
    projectpath = venvpath + '/' + 'imaginationforpeople' + '/'
    commonenv(projectpath, venvpath)
    env.wsginame = "staging.wsgi"
    env.urlhost = "staging.imaginationforpeople.org"
    require('venvpath', provided_by=('commonenv',))
    env.hosts = ['i4p-dev.imaginationforpeople.org']
    
    #env.gitbranch = "release/almostspring"
    env.gitbranch = "develop"
    #env.gitbranch = "feature/gis"

@task
def devenv(projectpath=None):
    """
    [ENVIRONMENT] Developpement (must be run from the project path: 
    the one where the fabfile is)
    """
    if not projectpath:
        projectpath = os.path.dirname(os.path.realpath(__file__))
    commonenv(projectpath,  getenv('VIRTUAL_ENV', None))
    env.wsginame = "dev.wsgi"
    env.urlhost = "localhost"
    env.user = env.local_user
    env.home = expanduser("~")
    require('venvpath', provided_by=('commonenv',))
    env.hosts = ['localhost']

    current_path = local('pwd',capture=True)
    
    env.gitrepo = "git@github.com:ImaginationForPeople/imaginationforpeople.git"
    env.gitbranch = "develop"


@task
def devenv2(projectpath=None):
    """
    [ENVIRONMENT] Developpement (must be run from the project path: 
    the one where the fabfile is)
    """
    if not projectpath:
        projectpath = os.path.dirname(os.path.realpath(__file__))
    commonenv(projectpath, getenv('VIRTUAL_ENV', None))
    env.wsginame = "dev.wsgi"
    env.urlhost = "localhost"
    #env.user = "webapp"
    #env.home = "webapp"
    require('venvpath', provided_by=('commonenv',))
    env.hosts = ['127.0.0.1']

    current_path = local('pwd',capture=True)
    
    env.gitrepo = "git@github.com:ImaginationForPeople/imaginationforpeople.git"
    env.gitbranch = "develop"

## Virtualenv
@task
def build_virtualenv():
    """
    Build the virtualenv
    """
    print(cyan('Creating a fresh virtualenv'))
    require('venvpath', provided_by=('commonenv'))
    sudo('rm /tmp/distribute* || echo "ok"') # clean after hudson
    run('virtualenv --no-site-packages --distribute %(venvpath)s' % env)
    sudo('rm /tmp/distribute* || echo "ok"') # clean after myself
    
def _get_package_list():
    """
    Get the list of currently installed packages and versions via pip freeze
    """
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):
        print(repr(env.hosts))
        return venvcmd("pip freeze -l")

def _execute_pip(cmd, dry_run=False):
    if dry_run:
        print "Dry run, would execute the following on host %s:" % (env.host_string)
        print cmd
        
    else:
        return venvcmd(cmd)
        
@task
def clone_package_versions(source=None, destination=None, dry_run=False):
    """
    Clone python packages between virtualenv ex: fab clone_package_versions:source='prodenv',destination='devenv',dry_run=True
    fab clone_environment:source='prodenv',destination='devenv' 
    """
    if dry_run == 'True':
        dry_run = True
    elif dry_run == 'False':
        dry_run = False
    print "Cloning environment %s to %s" % (source, destination)
    (packages, environments) = _check_package_versions([source, destination]);
    #WHATEVER YOU DO, do NOT remove this line.  Its the one that sets the 
    #Environment where pip commands will be executed.
    execute(destination)
    multi_versions = {}
    missing_servers = []
    for package, versions in packages.items():
        for version, version_info in versions.items():
            for host in version_info['environments']:
                if host == source:
                    source_version = version
                    pip_package_string = version_info['raw_package_string']
                elif host == destination:
                    destination_host = host
                    current_destination_version = version
        
        if len(versions.keys()) > 1:
            # There is more than one version installed on the servers
            print "Wrong version (%s) of package %s installed on %s.  Replacing with version %s"% (current_destination_version, package, destination, source_version)
            execute(_execute_pip, "pip install %s" % (pip_package_string), dry_run)
        elif len(versions[versions.keys()[0]]['environments']) != len(environments):
            # The package is not installed on all the environments
            missing_hosts = set(tuple(environments)) - set(versions[versions.keys()[0]]['environments'])
            for host in missing_hosts:
                if host == source:
                    print "Package %s installed on destination %s, but not on source %s.  Removing."% (package, destination, source)
                    execute(_execute_pip, "pip uninstall %s" % (package), dry_run)
                elif host == destination:
                    print "Package %s installed on source %s, missing on destination %s.  Installing."% (package, source, destination)
                    execute(_execute_pip, "pip install %s" % (pip_package_string), dry_run)


@task
def compare_package_versions(source=None, destination=None):
    """
    Compare python package versions on different environments ex: fab compare_package_versions:source='prodenv',destination='devenv'
    prints the out of sync packages
    """
    (packages, environments) = _check_package_versions([source, destination])
    return _process_packages(packages, environments)

@runs_once
def _check_package_versions(environments):
    """
    Check the versions of all the packages on all the servers and print out
    the out of sync packages
    """
    packages = {}
    for env_name in environments:
        env_task = globals()[env_name]
        execute(env_name)
        assert(len(env.hosts) == 1)
        #Only one host per env supported, as the goal is to compare environments

        print "Getting packages on %s for environment %s" % (env.hosts[0], env_name)
        result = execute(_get_package_list)[env.hosts[0]]
        pkg_list = result.splitlines()
        for package in pkg_list:
            if package.startswith("-e"):
                version, package_name = package.split("#egg=")
                index = package_name.find("-")
                if index:
                    pkg = package_name[:index]
                else:
                    pkg = package_name
            else:
                pkg, version = package.split("==")
            if pkg not in packages:
                packages[pkg] = {}
            if version not in packages[pkg]:
                packages[pkg][version] = {}
                packages[pkg][version]["environments"]=[]
            packages[pkg][version]["raw_package_string"]=package
            packages[pkg][version]["environments"].append(env_name)
    return (packages, environments)
    
def _process_packages(packages, environments):
    """
    Convert the packages datastructure into the multiple versions and missing
    servers lists and output the result
    """
    multi_versions = {}
    missing_servers = []
    for package, versions in packages.items():
        if len(versions.keys()) > 1:
            # There is more than one version installed on the servers
            multi_versions[package] = versions
        elif len(versions[versions.keys()[0]]['environments']) != len(environments):
            # The package is not installed on all the environments
            missing_hosts = set(tuple(environments)) - set(versions[versions.keys()[0]]['environments'])
            missing_servers.append(
                "%s: %s" % (package, ", ".join(missing_hosts))
            )
    if missing_servers or multi_versions:
        print ""
        print "Packages out-of-sync:"
    if multi_versions:
        print ""
        print "Multiple versions found of these packages:"
        for package, versions in multi_versions.items():
            print package
            for ver, version_info in versions.items():
                print "  %s: %s" % (ver, ", ".join(version_info['environments']))
    if missing_servers:
        print ""
        print "These packages are missing on these servers:"
        for item in missing_servers:
            print item

@task
def update_requirements(force=False):
    """
    update external dependencies on remote host
    """
    print(cyan('Updating requirements using PIP'))
    run('%(venvpath)s/bin/pip install -U pip' % env)
    
    if force:
        cmd = "%(venvpath)s/bin/pip install -I -r %(projectpath)s/requirements.txt" % env
    else:
        cmd = "%(venvpath)s/bin/pip install -r %(projectpath)s/requirements.txt" % env
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

@task
def make_messages():
    """
    Run *.po file generation for translation
    """
    appspath=env.projectpath + '/' + "apps"
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
    appspath=env.projectpath + '/' + "apps"
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
    with cd(env.projectpath + '/static'):
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
    with cd(env.projectpath):
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

    # Remove dir if necessary
    if exists(env.projectpath):
        sudo("rm -rf %(projectpath)s" % env)

    # Clone
    run("git clone --branch {0} {1} {2}".format(env.gitbranch,
                                                env.gitrepo,
                                                env.projectpath)
    )
    
            
def updatemaincode():
    """
    Update code and/or switch branch
    """
    print(cyan('Updating Git repository'))
    with cd(env.projectpath):
        run('git fetch')
        run('git checkout %s' % env.gitbranch)
        run('git pull %s %s' % (env.gitrepo, env.gitbranch))

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
def app_update_dependencies():
    execute(update_requirements, force=False)


@task
def app_fullupdate():
    """
    Full Update: maincode and dependencies
    """
    execute(updatemaincode)
    execute(app_update_dependencies)
    execute(app_compile)

@task
def app_update():
    """
    Fast Update: don't update requirements
    """
    execute(updatemaincode)
    execute(app_compile)

@task
def app_compile():
    """
    Generate every compiled resource, and update database schema
    """
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
    sudo('cp %sapache/%s /etc/apache2/sites-available/%s' % (env.projectpath, env.urlhost, env.urlhost))
    sudo('a2ensite %s' % env.urlhost)

    # nginx
    print(cyan('Configuring Nginx'))
    sudo('cp %snginx/%s /etc/nginx/sites-available/%s' % (env.projectpath, env.urlhost, env.urlhost))
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
    with cd(env.venvpath + '/'):
        sudo('mkdir -p logs/ ; chown www-data logs; chmod o+rwx logs ; pwd')


## Database server
def install_database_server():
    """
    Install a postgresql DB
    """
    print(cyan('Installing Postgresql'))
    sudo('apt-get install -y postgresql-8.4 postgresql-8.4 postgresql-8.4-postgis postgis')

def create_database_user():
    """
    Create a user and a DB for the project
    """
    # FIXME: pg_hba has to be changed by hand (see doc)
    # FIXME: Password has to be set by hand (see doc)
    sudo('createuser %s -D -R -S' % env.db_user, user='postgres')
    
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
    sudo('apt-get install -y build-essential pkg-config python-dev libjpeg62-dev libpng12-dev zlib1g-dev libfreetype6-dev liblcms-dev libpq-dev libxslt1-dev libxml2-dev graphviz libgraphviz-dev libgdal-dev')

@task
def install_rbenv():
    """
    Install the appropriate ruby environment for compass.
    """
    # Install rbenv:
    sudo('git clone git://github.com/sstephenson/rbenv.git ~/.rbenv', user=env.user)
    # Add rbenv to the path:
    sudo('echo \'export PATH="$HOME/.rbenv/bin:$PATH"\' >> .bash_profile', user=env.user)
    sudo('echo \'eval "$(rbenv init -)"\' >> .bash_profile', user=env.user)
    sudo('source ~/.bash_profile', user=env.user)
    # The above will work fine on a shell (such as on the server accessed using
    # ssh for a developement machine running a GUI, you may need to run the 
    # following from a shell (with your local user):
    #    echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.profile;
    #    echo 'eval "$(rbenv init -)"' >> ~/.profile;
    #    source ~/.profile;
    
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
    """
    (Re)Install compass, deleting current version 
    """
    with cd(env.projectpath):
        run('rm -rf vendor/bundle')
        execute(update_compass)
@task
def update_compass():
    """
    Make sure compass version is up to date
    """
    with cd(env.projectpath):
        run('pwd')
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
    
    execute(bootstrap_venv)
    
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
    with cd(env.projectpath):
        sudo('rm -rf media')
        run('scp -r web@i4p-prod.imaginationforpeople.org:/home/www/virtualenvs/imaginationforpeople.org/imaginationforpeople/media/ .')

        sudo('chown www-data -R media')
        sudo('chmod u+rw -R media')

def database_create():
    """
    """
    sudo('su - postgres -c "createdb -E UNICODE -Ttemplate0 -O%s %s"' % (env.db_user, env.db_name))

@task
def database_dump():
    """
    Dumps the database on remote site
    """
    if not exists(env.dbdumps_dir):
        run('mkdir -m700 %s' % env.dbdumps_dir)

    filename = 'db_%s.sql' % time.strftime('%Y%m%d')
    compressed_filename = '%s.postgisdump' % filename
    absolute_path = os.path.join(env.dbdumps_dir, compressed_filename)

    # Dump
    with prefix(venv_prefix()), cd(env.projectpath):
        run('grep "DATABASE" -A 8 site_settings.py')
        run('pg_dump -U%s --format=custom -b %s > %s' % (env.db_user,
                                                 env.db_name,
                                                 absolute_path)
            )

    # Make symlink to latest
    with cd(env.dbdumps_dir):
        run('ln -sf %s %s' % (absolute_path, remote_db_path()))
        
@task
def database_postgis_setup():
    """
    Setup or upgrade a database to postgis.  Normally run BEFORE restoring a 
    database dump, except the first time a postgis migration is done.
    """
    env.postgres_sharedir_path = run('pg_config --sharedir')
    env.postgis_script_path = os.path.join(env.postgres_sharedir_path, 'contrib/postgis-%s' % env.postgis_version)

    run('ls %s' % env.postgis_script_path)
    with settings(warn_only=True):
        sudo('su - postgres -c "createlang plpgsql %s"' % (env.db_name), shell=False)
    sudo('su - postgres -c "psql -d %s -f %s"' % (env.db_name, os.path.join(env.postgis_script_path, 'postgis.sql')), shell=False)
    sudo('su - postgres -c "psql -d %s -f %s"' % (env.db_name, os.path.join(env.postgis_script_path, 'spatial_ref_sys.sql')), shell=False)
    
    define_roles_sql = """CREATE ROLE postgis_reader INHERIT;
                            GRANT SELECT ON geometry_columns TO postgis_reader;
                            GRANT SELECT ON geography_columns TO postgis_reader;
                            GRANT SELECT ON spatial_ref_sys TO postgis_reader;
                            CREATE ROLE postgis_writer;
                            GRANT postgis_reader TO postgis_writer;
                            GRANT INSERT,UPDATE,DELETE ON spatial_ref_sys TO postgis_writer;
                            GRANT INSERT,UPDATE,DELETE ON geometry_columns TO postgis_writer;
                            GRANT INSERT,UPDATE,DELETE ON geography_columns TO postgis_writer;
                            GRANT postgis_writer TO imaginationforpeople;"""
    
    with settings(warn_only=True):
        sudo('su - postgres -c "psql %s -c %s"' % (env.db_name, pipes.quote(define_roles_sql)), shell=False)


@task    
def database_restore():
    assert(env.wsginame in ('staging.wsgi', 'dev.wsgi'))
    env.debug = True
    
    if(env.wsginame != 'dev.wsgi'):
        execute(webservers_stop)
    
    # Drop db
    with settings(warn_only=True):
        sudo('su - postgres -c "dropdb imaginationforpeople"')

    # Create db
    execute(database_create)
    execute(database_postgis_setup)

    # Restore data
#    with prefix(venv_prefix()), cd(env.projectpath):
#        run('grep "DATABASE" -A 8 site_settings.py')
#        run('bunzip2 -c %s | psql -U%s %s' % (remote_db_path(),
#                                              env.db_user,
#                                              env.db_name)
#        )
    # Restore data
    postgis_restore_script = os.path.join(env.projectpath, 'tools', 'postgis_restore-1.5.pl')
        
    run('%s %s %s %s' % (postgis_restore_script,
                                         os.path.join(env.postgis_script_path, 'postgis.sql'),
                                         env.db_name,
                                         remote_db_path())
        )
    drop_geometry_columns_sql = "DROP TABLE geometry_columns;"
    sudo('su - postgres -c "psql %s -c %s"' % (env.db_name, pipes.quote(drop_geometry_columns_sql)), shell=False)    
    drop_spatial_ref_sys_sql = "DROP TABLE spatial_ref_sys;"
    sudo('su - postgres -c "psql %s -c %s"' % (env.db_name, pipes.quote(drop_spatial_ref_sys_sql)), shell=False)    
    with prefix(venv_prefix()), cd(env.projectpath):
        run('grep "DATABASE" -A 8 site_settings.py')
    run('cat %s | psql -U%s %s' % (remote_db_path()+'.ascii',
                                              env.db_user,
                                              env.db_name)
        )

    if(env.wsginame != 'dev.wsgi'):
        execute(webservers_start)



@task
def database_download():
    """
    Dumps and downloads the database from the target server
    """
    execute(database_dump)
    get(remote_db_path(), 'current_database.sql.bz2')

@task
def database_upload():
    """
    Uploads a local database backup to the target environment's server
    """
    if(env.wsginame != 'dev.wsgi'):
        put('current_database.sql.bz2', remote_db_path())
