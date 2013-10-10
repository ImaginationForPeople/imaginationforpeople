from haystack import indexes

from .models import WorkGroup

class WorkGroupIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    description = indexes.CharField(model_attr='description', default='')
    language_code = indexes.CharField(model_attr='language')
    visible = indexes.BooleanField(model_attr='visible')    
    
    content_auto = indexes.EdgeNgramField(model_attr='name')

    # Fix for whoosh that messes with boolean types
    # See https://github.com/toastdriven/django-haystack/issues/382
    def prepare_visible(self, obj):
        if not obj.visible:
            return ''
        return 'True'
    
    def get_model(self):
        return WorkGroup

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()
