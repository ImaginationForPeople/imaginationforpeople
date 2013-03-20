from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from askbot.models.question import Thread

from apps.tags.models import TaggedCategory

class SpecificQuestionType(models.Model):
    key = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=30)
    allowed_category_tree = models.ForeignKey(TaggedCategory, null=True, blank=True)
    
    def __unicode__(self):
        return self.label

class SpecificQuestion(models.Model):
    type = models.ForeignKey(SpecificQuestionType)
    thread = models.ForeignKey(Thread)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    context_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ("type", "thread", "content_type", "object_id")
        