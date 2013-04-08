from haystack import indexes

from .models import I4pProjectTranslation

class I4pProjectTranslationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    baseline = indexes.CharField(model_attr='baseline')
    language_code = indexes.CharField(model_attr='language_code')
    slug = indexes.CharField(model_attr='slug')
    content_auto = indexes.EdgeNgramField(model_attr='title')
    sites = indexes.MultiValueField()
    
    def get_model(self):
        return I4pProjectTranslation

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
    
    def prepare_sites(self, obj):
        return [obj.id for obj in obj.master.site.all()]
