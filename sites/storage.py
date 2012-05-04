import os

from django.contrib.staticfiles.storage import FileSystemStorage
from django.utils.importlib import import_module

class SiteStaticStorage(FileSystemStorage):
    """
    A file system storage backend that takes a site module and works
    for the ``static`` directory of it.
    """
    prefix = None
    source_dir = 'static'

    def __init__(self, site, *args, **kwargs):
        """
        Returns a static file storage if available in the given site.
        """
        # site is the actual site module
        self.site_module = site
        mod = import_module(self.site_module)
        mod_path = os.path.dirname(mod.__file__)
        location = os.path.join(mod_path, self.source_dir)
        super(SiteStaticStorage, self).__init__(location, *args, **kwargs)







