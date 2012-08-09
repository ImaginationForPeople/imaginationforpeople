import os
import sys

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<name domain>'
    help = 'Manage multisites'
    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings
        try:
            name = args[0]
            domain = args[1]
        except Exception, e:
            raise CommandError("%s. Usage: %s." % (e, self.args))

        folder_name = domain.replace(".", "_").replace("-", "_")

        (site, was_created) = Site.objects.get_or_create(name=name, domain=domain, folder_name=folder_name)
        print('Successfully created or updated multisite "%s"' % site)

        print "====== APACHE"
        print
        
        # output a nice apache template
        apache_template_path = os.path.join(settings.PROJECT_ROOT, "apache", "multisite.wsgi.template")
        with open(apache_template_path, 'r') as f:
            template = f.read()

            variables = {}
            variables["VENV_PATH"] = os.environ.get('VIRTUAL_ENV')
            variables["PYTHON_VERSION"] = "%d.%d" % (sys.version_info.major, sys.version_info.minor)
            variables["SETTINGS_PATH"] = "imaginationforpeople.sites.%s" % site.folder_name

            for key, value in variables.items():
                template = template.replace("%%%s%%" % key, value)

            print
            print "============= Apache WSGI template ==============="
            print template
            print "============= End of Apache WSGI template ========"
            print

        # TODO list for the sysadmin
        print "====== WHAT YOU NEED TO DO NOW"
        print
        print "=> [I4P] Drop your multisite files into <%s>" % os.path.join(settings.PROJECT_ROOT, "sites", site.folder_name)
        print "=> [I4P] Don't forget to configure your site's <settings.py> (FACEBOOK API, etc)"
        print "=> [APACHE] Copy/Paste the WSGI code above to a file where your webserver can read"
        print "=> [APACHE] Add a virtualhost that points to this WSGI file and enable it"
        print "=> [NGINX] If you use Nginx, add <%s> to the domains of NGINX" % site.domain        
        print "=> [WEBSERVERS] Restart your webservers"        
        print