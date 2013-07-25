'''
Created on 2013-06-05

@author: benoitg
'''
from django.core.management.base import BaseCommand, CommandError
from apps.i4p_base.models import Location
from apps.i4p_base.forms import I4pLocationForm
from optparse import make_option
from time import sleep

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Run blind geoding on locations matching criterias'
    option_list = BaseCommand.option_list + (
        make_option('--location-criteria',
            action='store_true',
            dest='location-criteria',
            default='ADRESS_NOGEOM',
            help='Criteria used to select locations whose geom will be owerwritten\n' + 
            'Choice of:' + 
            'ADRESS_NOLOC: Default, geocode locations with a non-empty adress but no geometry'
            ),
        )

    def handle(self, *args, **options):
        location_qs = Location.objects
        modified_location_count = 0
        if args:
            location_qs = location_qs.filter(pk__in=args)
        if options['location-criteria']=='ADRESS_NOGEOM':
            location_qs = location_qs.filter(geom__isnull=True)
            location_qs = location_qs.filter(address__isnull=False).exclude(address__exact='')
        #location_qs = location_qs[:5]
        try:
            for location in location_qs:
                self.stdout.write('\n\nGeocoding location %d:\n' % location.id)
                self.stdout.write('%s' % location.address)
                #country = location.country.name
                geocode_results = I4pLocationForm.geocode(location.address);
                geocode_results_count = I4pLocationForm.count_geocode_results(geocode_results, exact_only=True)
                if geocode_results_count == 1:
                    for geocoder_result in geocode_results.values():
                        if not 'error' in geocoder_result.keys():
                            for result in geocoder_result['result_list']:
                                # We know will execute this line once (there was
                                # only one result).
                                self.stdout.write('\nResult: %s' % result['geom'])
                                location.geom=result['geom']
                                location.save()
                                modified_location_count+=1
                else:
                    self.stdout.write('\nResult: FAILED: %d locations were returned by the geocoders.' % geocode_results_count)
                    for geocoder_result in geocode_results.values():
                        if 'error' in geocoder_result.keys():
                            geocoder_name = unicode(geocoder_result['geocoder_description']['name'])
                            self.stdout.write('\nError: %s returned error: %s.' % (geocoder_name, geocoder_result['error']))
                sleep(1);

        except Location.DoesNotExist:
                raise CommandError('\nNo location matching criteria found')

        self.stdout.write('\nGeocoding on %d locations finished.  %d locations modified' % (len(location_qs),modified_location_count))
