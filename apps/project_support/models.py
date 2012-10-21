from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.project_sheet.models import I4pProjectTranslation
from askbot.models.question import Thread
from apps.tags.models import TaggedCategory

SUPPORT_TYPE_CHOICES = (
    ("CALL", _("call for help")),
    ("PROP", _("help proposal")),
)

class ProjectSupport(models.Model):
    project_translation = models.ForeignKey(I4pProjectTranslation)
    type = models.CharField(max_length=4, choices=SUPPORT_TYPE_CHOICES)
    category = models.ForeignKey(TaggedCategory)
    thread = models.ForeignKey(Thread)

    def get_absolute_url(self):
        return reverse("project_support_view", args=[self.project_translation.slug, self.thread.question.id])
    
    
    