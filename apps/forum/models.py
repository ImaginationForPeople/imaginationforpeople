from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from askbot.models.question import Thread, FavoriteQuestion

from apps.tags.models import TaggedCategory

import datetime
from askbot.models.post import Post
from askbot.tasks import record_post_update
from askbot.models import send_instant_notifications_about_activity_in_post
from askbot.const import TYPE_ACTIVITY_ASK_QUESTION
from askbot.models.user import Activity


QUESTION_TYPE_CHOICES = (
    ('generic', _('generic')),
    ('pj-need', _('project needs')),
    ('pj-help', _('help from the community')),
    ('pj-discuss', _('project discussion')),
    ('wg-discuss', _('workgroup discussion')),
)


class SpecificQuestionType(models.Model):
    type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, unique=True, null=True)
    allowed_category_tree = models.ForeignKey(TaggedCategory, null=True, blank=True)
    picto = models.ImageField(upload_to="question_picto/", null=True, blank=True)
    
    def __unicode__(self):
        return self.get_type_display()

class SpecificQuestion(models.Model):
    """
    A specific question is a concept that wrap a askbot thread in order to use it 
    in a other context (represented by the GFK context_object)
    such as project sheet, workgroup, tag pages, etc.
    """
    type = models.ForeignKey(SpecificQuestionType, related_name="specific_questions")
    thread = models.ForeignKey(Thread)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    context_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ("type", "thread", "content_type", "object_id")

@receiver(post_delete, sender=SpecificQuestion)
def purge_specific_thread(sender, instance, **kwargs):
    """
    if a thread is specific is not visible in the global forum, so if
    the wrapping specific question is deleted the wrapped thread too, in order
    to avoid ghost thread.
    """
    if instance.thread.is_specific:
        instance.thread.delete()

@receiver(post_save, sender=Activity)
def subscribe_context_object_members(sender, instance, created, **kwargs):
    activity = instance
    
    if activity.content_type == ContentType.objects.get_for_model(Post) \
       and activity.activity_type == TYPE_ACTIVITY_ASK_QUESTION:
        
        if activity.content_object.thread.specificquestion_set.count():
            specific_question = activity.content_object.thread.specificquestion_set.all()[0] #FIXME: may have side effet
            context = specific_question.context_object
            
            if hasattr(context, 'get_members') \
               and hasattr(context, 'mail_auto_subscription') \
               and context.mail_auto_subscription:
                
                recipients = []
                for member in context.get_members():
                    if not isinstance(member, User):
                        member = member.user
                    recipients.append(member)
                
                send_instant_notifications_about_activity_in_post(activity, 
                                                                  post=activity.content_object, 
                                                                  recipients=recipients)
                            