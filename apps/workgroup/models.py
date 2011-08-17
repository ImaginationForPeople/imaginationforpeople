from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug.fields import AutoSlugField

from django_mailman.models import List

class WorkGroup(models.Model):
    """
    A workgroup in a given language, for a given thematic.
    """
    slug = AutoSlugField(populate_from='name',
                         always_update=True)

    name = models.CharField(verbose_name=_('name'),
                            max_length=150)

    language = models.CharField(verbose_name=_('spoken language'),
                                max_length=2,
                                choices=settings.LANGUAGES)

    description = models.TextField(verbose_name=_('Description'),
                                   null=True,
                                   blank=True)
    
    mailing_list = models.ForeignKey(List, 
                                     default=None, 
                                     null=True, blank=True)


    def __unicode__(self):
        return u"%s (%s)" % (self.name,
                             self.get_language_display())


    @models.permalink
    def get_absolute_url(self):
        return ('workgroup-detail', (self.slug,))

    
