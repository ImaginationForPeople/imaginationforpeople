from django.conf import settings
from django.utils.encoding import force_unicode

from haystack import indexes
from haystack.constants import ID, DJANGO_CT, DJANGO_ID

from .models import I4pProject

class I4pProjectIndex(indexes.SearchIndex, indexes.Indexable):
    #text = indexes.MultiValueField(document=True, use_template=False)
    text = indexes.CharField(document=True, use_template=False)
    #title = indexes.CharField(model_attr='title')
    #baseline = indexes.CharField(model_attr='baseline')
    #For some reason MultiValueField doesn't work properly with whoosh, language_codes
    #language_code = indexes.CharField(model_attr='language_code')
    language_codes = indexes.MultiValueField(indexed=True, stored=True)
    #slug = indexes.CharField(model_attr='slug')
    content_auto = indexes.EdgeNgramField(model_attr='title')
    best_of = indexes.BooleanField(model_attr='best_of')
    sites = indexes.MultiValueField()
    tags = indexes.MultiValueField(indexed=True, stored=True, model_attr='themes')
    location = indexes.CharField()
    has_team = indexes.BooleanField()
    has_needs = indexes.BooleanField()
    created = indexes.DateTimeField(model_attr='created')
    
    def get_model(self):
        return I4pProject

    def read_queryset(self, using=None):
        return I4pProject.objects.untranslated().all()
        
    def prepare_sites(self, obj):
        return [obj.id for obj in obj.site.all()]

    def prepare_language_codes(self, obj):
        return obj.get_available_languages()

    def prepare_text(self, obj):
        """
        The textual content of the project
        """
        languages = obj.get_available_languages()
        retval = []
        for language in languages:
            translated_obj = self.get_model().objects.language(language).get(pk=obj.pk)
            retval.append(' '.join((translated_obj.title, translated_obj.baseline)))
        return ' '.join(retval)
    def prepare_has_team(self, obj):
        """
        If there is at least one user associated with this project
        """
        return obj.members.count() > 0

    def prepare_has_needs(self, obj):
        """
        If the project has expressed needs
        """
        return obj.lazy_translation_getter('projectsupport_set').count() > 0

    def prepare_tags(self, obj):
        """
        Split tags by comma
        """
        return obj.themes.split(',')

    def prepare_location(self, obj):
        if obj.location:
            return obj.location.country.code
        else:
            return None
