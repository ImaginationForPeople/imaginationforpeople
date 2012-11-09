from haystack import indexes

from .models import I4pProjectTranslation

class I4pProjectTranslationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    baseline = indexes.CharField(model_attr='baseline')
    language_code = indexes.CharField(model_attr='language_code')
    content_auto = indexes.EdgeNgramField(model_attr='title')

    def get_model(self):
        return I4pProjectTranslation

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
