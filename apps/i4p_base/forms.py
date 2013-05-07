from django import forms
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from haystack.forms import FacetedSearchForm

class ProjectSearchForm(FacetedSearchForm):
    q = forms.CharField(required=False, label=_('Search'))
    best_of = forms.BooleanField(required=False, label=_('Best of'))
    has_team = forms.BooleanField(required=False, label=_('Has team'))
    has_needs = forms.BooleanField(required=False, label=_('Has needs'))
    location = forms.CharField(required=False, label=_('Location'))
    language_code = forms.CharField(required=False, label=_('Language'))
    tags = forms.CharField(required=False, label=_('Tags'))    
    
    def search(self):
        sqs = self.searchqueryset
        
        if not self.is_valid():
            # FIXME Would need a random here
            language_code = translation.get_language()
            return sqs.filter(language_code=language_code)

        if self.cleaned_data.get('q'):
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        # I4P Project sheet criteria
        filters = {}
        for field in ('best_of', 'has_team', 'has_needs', 'location', 'language_code', 'tags'):
            data = self.cleaned_data.get(field)
            if data and data != "":
                filters[field] = self.cleaned_data[field]

        sqs = sqs.filter(**filters)
            
        if self.load_all:
            sqs = sqs.load_all()

        return sqs
