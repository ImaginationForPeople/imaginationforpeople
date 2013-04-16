from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from askbot.models.question import Thread

from apps.tags.models import TaggedCategory
from django.utils.translation import ugettext_lazy as _

QUESTION_TYPE_CHOICES = (
    ('generic', _('generic')),
    ('pj-need', _('project needs')),
    ('pj-help', _('help from the community')),
    ('pj-discuss', _('project discussion')),
    ('wg-discuss', _('workgroup discussion')),
)


class SpecificQuestionType(models.Model):
    #key = models.CharField(max_length=30, unique=True)
    #label = models.CharField(max_length=30)
    type = models.CharField(max_length="10", choices=QUESTION_TYPE_CHOICES, unique=True, null=True)
    allowed_category_tree = models.ForeignKey(TaggedCategory, null=True, blank=True)
    picto = models.ImageField(upload_to="question_picto/", null=True, blank=True)
    
    def __unicode__(self):
        return self.get_type_display()

class SpecificQuestion(models.Model):
    type = models.ForeignKey(SpecificQuestionType)
    thread = models.ForeignKey(Thread)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    context_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ("type", "thread", "content_type", "object_id")
        