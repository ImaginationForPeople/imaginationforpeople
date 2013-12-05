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
	#print loc
	lang = obj.thread.language_code
	regex = re.compile(r"^\/(en)\/")
        return regex.sub(r"/"+lang+"/",loc)
