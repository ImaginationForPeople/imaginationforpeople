import floppyforms as forms
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from haystack.forms import FacetedSearchForm
from django.forms.models import modelformset_factory
from django.forms.formsets import DELETION_FIELD_NAME

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
    language_codes = forms.CharField(required=False, label=_('Language'))
    tags = forms.CharField(required=False, label=_('Tags'))    
    order = forms.CharField(required=False, label=_('Order')) 
    status = forms.CharField(required=False, label=_('Status'), widget=forms.widgets.HiddenInput) 
        
    def search(self):
        sqs = self.searchqueryset
        
        if not self.is_valid():
            # FIXME Would need a random here
            return sqs.load_all().order_by('?')

        if self.cleaned_data.get('q'):
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        # I4P Project sheet criteria
        filters = {}
        for field in ('best_of', 'has_team', 'has_needs', 'countries', 'language_codes', 'tags', 'status'):
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
    """
    A non database field to represent geocoder results
    """
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
    geocode_picker = GeocodeResultPickerField(required=False,
                                              help_text=_("Multiple results were found.  Please chose the best one (you can refine it afterwards using the map)")
                                              )
    force_geocode = forms.BooleanField(required=False,
                                       widget=forms.widgets.HiddenInput,
                                       initial=False
                                       )
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
        geocode_picker_data = cleaned_data.get("geocode_picker")
        if geocode_picker_data:
            #This replaces the map information, will be saved later
            changed_geom=geocode_picker_data
        elif address and (not geom or cleaned_data.get("force_geocode")):
            # Only geocode if we haven't already set a map, or forced geocoding
            geocode_results = self.geocode(address)
            geocode_results_count = self.count_geocode_results(geocode_results)
            if geocode_results_count == 1:
                for geocoder_result in geocode_results.values():
                    if not 'error' in geocoder_result.keys():
                        for result in geocoder_result['result_list']:
                            # We know will execute this line once (there was
                            # only one result).
                            changed_geom=result['geom']
            else:
                self._errors["geocode_picker"] = self.error_class([_('%d locations were returned by the geocoders, please select the most appropriate one.  You can refine in the map after saving if none are appropriate.') % geocode_results_count])
                if 'cleaned_data' in cleaned_data.keys():
                    del(cleaned_data["geocode_picker"])
                self.fill_geocode_picker(geocode_results)


        if changed_geom:
            # We replace the map information, will be saved later
            cleaned_data['geom']=changed_geom
        if not geocode_results:
            del self.fields['geocode_picker']
        #Reset force geocoding
        # Yes, it's insane, and yes, it's the least insane choice in django
        # http://stackoverflow.com/questions/4662848/disabled-field-is-not-passed-through-workaround-needed/4664866#4664866
        self.data=self.data.copy()
        self.data['force_geocode']=False
        return cleaned_data
    
    def save(self, *args, **kwargs):
        retval = super(I4pLocationForm, self).save(*args, **kwargs)
        # Yes, it's insane, and yes, it's the least insane choice in django
        # http://stackoverflow.com/questions/4662848/disabled-field-is-not-passed-through-workaround-needed/4664866#4664866
        self.data=self.data.copy()
        if self.instance.geom:
            self.data['geom']=self.instance.geom.ewkt
        else:
            self.data['geom']=None
        self.data['geocode_picker']=''
        return retval
    
    @staticmethod
    def count_geocode_results(geocode_results, exact_only=False):
        if(exact_only):
            results = [v for v in geocode_results.values() if v['geocoder_description']['is_exact']==True]
        else:
            results = geocode_results.values()
        return sum([len(v['result_list']) for v in results])

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
    @staticmethod
    def get_active_geocoders():
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
        return active_geocoders
    @staticmethod    
    def geocode(addr, **kwargs):
        results = {}
        active_geocoders=I4pLocationForm.get_active_geocoders();
        # The result first Geocoder with is_exact=true to return exactly one
        # result (if any) will be silently used as coordinates.
        # The reason we don't simply use the first one that returns exactly one
        # result is that some (such as mapquest) return only the street for
        # non-us adresses

        for geocoder_description in active_geocoders:
            geocoder_name = geocoder_description['name']
            results[geocoder_name]={}
            results[geocoder_name]['result_list']=[]
            results[geocoder_name]['geocoder_description']=geocoder_description
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
                            results[geocoder_name]['geocoder_description']=geocoder_description
                            results[geocoder_name]['result_list']=[]
                            results[geocoder_name]['result_list'].append({'place' : place, 'geom': geom})
                            return results
                        else:
                            results[geocoder_name]['result_list'].append({'place' : place, 'geom': geom})
                        
                            
            except GeocoderResultError as error:
                results[geocoder_name]['error'] = str(error)
            except Exception as error:
                #This should normally be caught by geopy, but isn't sometimes
                results[geocoder_name]['error'] = str(error)
        return results

BaseI4pLocationFormSet = modelformset_factory(Location,
                                                 extra=1,
                                                 can_delete=True,
                                                 form=I4pLocationForm
                                                 )

class I4pLocationFormSet(BaseI4pLocationFormSet):
    def add_fields(self, form, index):
        super(I4pLocationFormSet, self).add_fields(form,index)
        form.fields[DELETION_FIELD_NAME].widget = forms.HiddenInput()
