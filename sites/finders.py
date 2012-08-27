import os, sys

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.utils.datastructures import SortedDict


from .storage import SiteStaticStorage

class SiteDirectoriesFinder(BaseFinder):
    """
    A static files finder that looks in the directory of each sites as
    specified in the source_dir attribute of the given storage class.
    """
    storage_class = SiteStaticStorage

    def __init__(self, sites=None, *args, **kwargs):
        # The list of sites that are handled
        self.sites = []
        # Mapping of site module paths to storage instances
        self.storages = SortedDict()

        # First, add the site dir to the path
        sys.path.append(settings.SITES_DIR)

        # Look up sites from the database
        if sites is None:
            sites = [site.folder_name for site in Site.objects.all() if site.folder_name not in (None, '')]

        for site in sites:
            site_storage = self.storage_class(site)
            if os.path.isdir(site_storage.location):
                self.storages[site] = site_storage
                if site not in self.sites:
                    self.sites.append(site)

        super(SiteDirectoriesFinder, self).__init__(*args, **kwargs)

    def list(self, ignore_patterns):
        """
        List all files in all site storages.
        """
        for storage in self.storages.itervalues():
            if storage.exists(''): # check if storage location exists
                for path in utils.get_files(storage, ignore_patterns):
                    yield path, storage

    def find(self, path, all=False):
        """
        Looks for files in the site directories.
        """
        matches = []
        for site in self.sites:
            match = self.find_in_site(site, path)
            if match:
                if not all:
                    return match
                matches.append(match)
        return matches

    def find_in_site(self, site, path):
        """
        Find a requested static file in an site's static locations.
        """
        storage = self.storages.get(site, None)
        if storage:
            if storage.prefix:
                prefix = '%s%s' % (storage.prefix, os.sep)
                if not path.startswith(prefix):
                    return None
                path = path[len(prefix):]
            # only try to find a file if the source dir actually exists
            if storage.exists(path):
                matched_path = storage.path(path)
                if matched_path:
                    return matched_path






