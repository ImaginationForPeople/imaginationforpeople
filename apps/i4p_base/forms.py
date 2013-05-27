import floppyforms as forms
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from haystack.forms import FacetedSearchForm
from django.forms.models import modelformset_factory
from django.forms.widgets import HiddenInput

from .models import Location
from geopy import geocoders
from geopy.geocoders.base import  GeocoderResultError

from django.contrib.gis.geos.point import Point
from django.contrib.gis.geos import GEOSGeometry
from settings import MAPQUEST_API_KEY, GEONAMES_USERNAME

class ProjectSearchForm(FacetedSearchForm):
    q = forms.CharField(required=False, label=_('Search'))
    best_of = forms.BooleanField(required=False, label=_('Best of'))
    has_team = forms.BooleanField(required=False, label=_('Has team'))
    has_needs = forms.BooleanField(required=False, label=_('Has needs'))
    countries = forms.CharField(required=False, label=_('Location'))
    language_code = forms.CharField(required=False, label=_('Language'))
    tags = forms.CharField(required=False, label=_('Tags'))    
    order = forms.CharField(required=False, label=_('Order')) 
    
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
        for field in ('best_of', 'has_team', 'has_needs', 'countries', 'language_code', 'tags'):
            data = self.cleaned_data.get(field)
            if data and data != "":
                filters[field] = self.cleaned_data[field]

        sqs = sqs.filter(**filters)
            
        if self.load_all:
            sqs = sqs.load_all()

        return sqs
    
    
class OsmPointWidget(forms.gis.BaseGMapWidget,
                          forms.gis.PointWidget):
    pass

class GeocodeResultPickerField(forms.ChoiceField):
    #widget = forms.widgets.Select
    #widget = forms.widgets.HiddenInput
    def to_python(self, value):
        "Normalize data to a Point or none."

        # Return an empty list if no input was given.
        if not value:
            return None
        return GEOSGeometry(value)

    def validate(self, value):
        "Check if value is a valid Point."

        isinstance(value, Point)



class I4pLocationForm(forms.ModelForm):
    """
    Edit the location info of an Object
    """
    geocode_picker = GeocodeResultPickerField(required=False)
    def __init__(self, *args, **kwargs):
        super(I4pLocationForm, self).__init__(*args, **kwargs)
        self.fields['country'].required = True
        if not self.is_bound:
            del self.fields['geocode_picker']
            
    class Meta:
        model = Location
        fields = ('country', 'address', 'geocode_picker', 'geom',)
        widgets={'geom': OsmPointWidget(),
                 }

    def clean(self):
        cleaned_data = super(I4pLocationForm, self).clean()
        geom = cleaned_data.get('geom')
        changed_geom = None
        geocode_results = None
        address = cleaned_data.get("address")
        if address and not geom:
            # Only geocode if we haven't already set a map.
            geocode_picker_data = cleaned_data.get("geocode_picker")
            
            if not geocode_picker_data:
                geocode_results = self.geocode(address)
                geocode_results_count = self.count_results(geocode_results)
                if geocode_results_count == 1:
                    for geocoder_result in geocode_results.values():
                        if not 'error' in geocoder_result.keys():
                            for result in geocoder_result['result_list']:
                                # We know will execute this line once (there was
                                # only one result.
                                changed_geom=result['geom']
                else:
                    self._errors["geocode_picker"] = self.error_class([_('%d locations were returned by the geocoders, please select the most appropriate one.  You may also select from the map below if none are appropriate.') % geocode_results_count])
                    if 'cleaned_data' in cleaned_data.keys():
                        del(cleaned_data["geocode_picker"])
                    self.fill_geocode_picker(geocode_results)
            else:
                #This replaces the map information, will be saved later
                changed_geom=geocode_picker_data

        if changed_geom:
            # We replace the map information, will be saved later
            cleaned_data['geom']=changed_geom
        if not geocode_results:
            del self.fields['geocode_picker']
        #data=self.data
        #raise ValueError('DOH')
        return cleaned_data

    def count_results(self, geocode_results):
        return sum([len(v['result_list']) for v in geocode_results.values()])

    def fill_geocode_picker(self, geocode_results):
        choices=[]
        for geocoder_name, geocoder_result in geocode_results.iteritems():

            if 'error' in geocoder_result.keys():
                choices.append([
                    geocoder_name + ': ' + geocoder_result['error'], []
                    ]) 
            else:
                result_list=[]
                for result in geocoder_result['result_list']:
                    result_list.append([result['geom'].wkt, result['place']])
                choices.append([
                    geocoder_name, result_list
                    ])
        self.fields['geocode_picker'].choices = choices
        
    def geocode(self, addr, **kwargs):
        results = {}
        # The result first Geocoder with is_exact=true to return exactly one
        # result (if any) will be silently used as coordinates.
        # The reason we don't simply use the first one that returns exactly one
        # result is that some (such as mapquest) return only the street for
        # non-us adresses
        active_geocoders = []
        active_geocoders.append({'name': _('Google geocoder'),
                                 'geocoder': geocoders.GoogleV3(),
                                 'is_exact': True,
                                })
        if MAPQUEST_API_KEY:
            active_geocoders.append({'name': _('MapQuest geocoder'),
                                 'geocoder': geocoders.MapQuest(api_key=MAPQUEST_API_KEY),
                                 'is_exact': False,
                                })
        if GEONAMES_USERNAME:
            active_geocoders.append({'name': _('Geonames places database'),
                                 'geocoder': geocoders.GeoNames(username=GEONAMES_USERNAME),
                                 'is_exact': False,
                                })
        active_geocoders.append({'name': _('Nominatim database'),
                                 'geocoder': geocoders.OpenMapQuest(),
                                 'is_exact': False,
                                })
        for geocoder_description in active_geocoders:
            geocoder_name = geocoder_description['name']
            results[geocoder_name]={}
            results[geocoder_name]['result_list']=[]
            
            try:
                query_result = geocoder_description['geocoder'].geocode(addr, exactly_one=False)
                if query_result:
                    result_count = len(query_result)
                    for place, (lat, lng) in query_result:
                        geom = Point(lng, lat)
                        if result_count == 1 and geocoder_description['is_exact']:
                            # We have an unambiguous result
                            results = {}
                            results[geocoder_name]={}
                            results[geocoder_name]['result_list']=[]
                            results[geocoder_name]['result_list'].append({'place' : place, 'geom': geom})
                            return results
                        else:
                            results[geocoder_name]['result_list'].append({'place' : place, 'geom': geom})
                        
                            
            except GeocoderResultError as error:
                results[geocoder_name]['error'] = str(error)
        return results

I4pLocationFormSet = modelformset_factory(Location,
                                                 extra=1,
                                                 can_delete=True,
                                                 form=I4pLocationForm
                                                 )
