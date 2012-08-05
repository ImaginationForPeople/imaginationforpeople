from haystack import indexes

from .models import I4pProfile

class I4pProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='get_full_name_or_username')
    content_auto = indexes.EdgeNgramField(model_attr='get_full_name_or_username')

    def get_model(self):
        return I4pProfile

    def index_queryset(self):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()