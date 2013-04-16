from django import forms
from django.utils.translation import ugettext_lazy as _

from haystack.forms import FacetedSearchForm

class ProjectSearchForm(FacetedSearchForm):
    q = forms.CharField(required=False, label=_('Search'), initial='')
    best_of = forms.BooleanField(required=False, label=_('Best of'))
    has_team = forms.BooleanField(required=False, label=_('Has team'))    
    
    def search(self):
        sqs = self.searchqueryset
        
        if not self.is_valid():
            print "NOT VALID", self.errors
            return self.no_query_found()

        if self.cleaned_data.get('q'):
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        # I4P Project sheet criterions
        if self.cleaned_data.get('best_of'):
            sqs = sqs.filter(best_of=self.cleaned_data['best_of'])

        if self.cleaned_data.get('has_team'):
            sqs = sqs.filter(has_team=self.cleaned_data['has_team'])

        if self.load_all:
            sqs = sqs.load_all()

        print len(sqs)

        return sqs
