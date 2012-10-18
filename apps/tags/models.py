from django.db import models
from askbot.models import Tag
from categories.models import CategoryBase
from django.db.models.signals import pre_save

# Create your models here.
class TaggedCategory(CategoryBase):
    tag = models.OneToOneField(Tag)
    

def first_tag_association(sender, instance, **kwargs):
    if instance.tag == None:
        tag, created = Tag.objects.get_or_create(name=instance.slug)
        instance.tag = tag

pre_save.connect(first_tag_association, TaggedCategory)