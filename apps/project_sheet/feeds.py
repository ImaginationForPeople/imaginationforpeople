import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.utils import translation

from localeurl.models import reverse
from reversion.models import Version

from .models import I4pProject, I4pProjectTranslation
from .utils import get_project_project_translation_recent_changes
from .utils import get_project_translations_from_parents

class LatestChangesFeed(Feed):
    """
    A feed for displaying the latest changes of the project sheets
    """
    title = "Imagination For People latest changes"
    description = "Latest changes in the projects"
    
    def items(self):
        twenty_days_ago = datetime.datetime.now() - datetime.timedelta(days=20)

        project_translation_ct = ContentType.objects.get_for_model(I4pProjectTranslation)
        parent_project_ct = ContentType.objects.get_for_model(I4pProject)
        
        versions = Version.objects.filter(Q(content_type=project_translation_ct) | Q(content_type=parent_project_ct)).filter(revision__date_created__gt=twenty_days_ago).order_by('-revision__date_created')

        return get_project_project_translation_recent_changes(versions)
    

    def item_title(self, item):
        return item['object'].title

    def item_description(self, item):
        return ", ".join(item['diff'])

    def item_pubdate(self, item):
        return item['revision'].date_created

    def item_link(self, item):
        return reverse('project_sheet-show', kwargs={'slug': item['slug'], 'locale': item['language_code']})

    def link(self):
        return reverse('project_sheet-recent-changes')


class NewProjectsFeed(Feed):
    """
    A feed displaying the newest projects
    """
    title = 'New projects on Imagination For People'
    description = 'Most recent projects added to the website'

    def items(self):
        language_code = translation.get_language()
        return get_project_translations_from_parents(parents_qs=I4pProject.objects.all().order_by('-created')[:20],
                                                     language_code=language_code,
                                                     fallback_language='en',
                                                     fallback_any=True)

    def link(self):
        return reverse('project_sheet-list')


    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.baseline

    def item_pubdate(self, item):
        return item.project.created

