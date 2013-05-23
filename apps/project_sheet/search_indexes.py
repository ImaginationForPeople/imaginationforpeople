from django.conf import settings
from django.utils.encoding import force_unicode

from haystack import indexes
from haystack.constants import ID, DJANGO_CT, DJANGO_ID

from .models import I4pProject

class I4pProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    baseline = indexes.CharField(model_attr='baseline')
    language_code = indexes.CharField(model_attr='language_code')
    slug = indexes.CharField(model_attr='slug')
    content_auto = indexes.EdgeNgramField(model_attr='title')
    best_of = indexes.BooleanField(model_attr='best_of')
    sites = indexes.MultiValueField()
    tags = indexes.MultiValueField(indexed=True, stored=True, model_attr='themes')
    countries = indexes.MultiValueField(indexed=True, stored=True)
    has_team = indexes.BooleanField()
    has_needs = indexes.BooleanField()
    created = indexes.DateTimeField(model_attr='created')
    
    def get_model(self):
        return I4pProject

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        
        We loop over all the declared languages to index the
        variations of every Hvad translations.
        """
        queryset = I4pProject.objects.none()
        for language_code, language_desc in settings.LANGUAGES:
            language_queryset = self.get_model().objects.language(language_code).all()
            queryset |= language_queryset

        return queryset

    def read_queryset(self, using=None):
        return I4pProject.objects.all()

    def prepare(self, obj):
        """Fetches and adds/alters data before indexing.

        HACKY: I had to update the "ID" field so that it suffixes the
        language code. For example, "i4pproject.145" becomes
        "i4pproject.145-fr" and so can be indexed as many times as
        there are language variations -- @glibersat.
        """
        self.prepared_data = {
            ID: u"%s.%s.%s-%s" % (obj._meta.app_label, obj._meta.module_name, obj._get_pk_val(), obj.language_code), # The change is here
            DJANGO_CT: "%s.%s" % (obj._meta.app_label, obj._meta.module_name),
            DJANGO_ID: force_unicode(obj.pk),
        }

        for field_name, field in self.fields.items():
            # Use the possibly overridden name, which will default to the
            # variable name of the field.
            self.prepared_data[field.index_fieldname] = field.prepare(obj)

            if hasattr(self, "prepare_%s" % field_name):
                value = getattr(self, "prepare_%s" % field_name)(obj)
                self.prepared_data[field.index_fieldname] = value

        return self.prepared_data
        
    def prepare_sites(self, obj):
        return [obj.id for obj in obj.site.all()]

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

    def prepare_countries(self, obj):
        if obj.locations:
            return [location.country.code for location in obj.locations.all()]
        else:
            return None
