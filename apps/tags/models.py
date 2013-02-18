from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save

from askbot.models import Tag
from categories.models import CategoryBase


# Create your models here.
class TaggedCategory(CategoryBase):
    tag = models.OneToOneField(Tag)
    

def first_tag_association(sender, instance, **kwargs):
    try:
        tag = Tag.objects.get(name=instance.slug)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(name=instance.slug, 
                                 created_by=User.objects.get(id=settings.ANONYMOUS_USER_ID))
    instance.tag = tag

pre_save.connect(first_tag_association, TaggedCategory)