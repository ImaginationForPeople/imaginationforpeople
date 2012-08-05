from haystack import indexes

from .models import WorkGroup

class WorkGroupIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    description = indexes.CharField(model_attr='description')
    language_code = indexes.CharField(model_attr='language')
    
    content_auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return WorkGroup

    def index_queryset(self):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()