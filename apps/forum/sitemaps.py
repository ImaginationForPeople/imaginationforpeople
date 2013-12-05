import re

from django.contrib.sitemaps import Sitemap
from askbot.models import Post

class QuestionsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5
    def items(self):
        return Post.objects.get_questions().exclude(deleted=True)

    def lastmod(self, obj):
        return obj.thread.last_activity_at

    def location(self, obj):
        loc = obj.get_absolute_url()
	lang = obj.thread.language_code
        regex = re.compile(r"^\/[a-z]{2}\/") # look for the 2 letters default lang code and replace it with actual one
        return regex.sub(r"/"+lang+"/",loc)
