from django.contrib.sitemaps import Sitemap

from .models import I4pProjectTranslation

class I4pProjectTranslationSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return I4pProjectTranslation.objects.all()

    def lastmod(self, obj):
        return obj.modified
