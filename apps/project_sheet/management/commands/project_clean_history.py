import os
import sys

import reversion
import json

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Clean project history'
    can_import_settings = True

    def handle(self, *args, **options):
        from apps.project_sheet.models import I4pProjectTranslation

        model_fields = [field.name for field in I4pProjectTranslation._meta.fields]
        
        for translation in I4pProjectTranslation.objects.all():
            print "Inspecting %s" % translation
            versions = reversion.get_for_object(translation)
            for v in versions:
                print "\t- %s" % v
                j = json.loads(v.serialized_data)
                json_fields = j[0]['fields']

                # Collect fields to delete
                fields_to_delete = []
                for json_field in json_fields:
                    if json_field not in model_fields:
                        print "\t\t [-] Removing field <%s>" % json_field
                        fields_to_delete.append(json_field)

                if len(fields_to_delete) > 0:
                    # Now remove them (this can't be done in one pass
                    # since the dictionary size would change)
                    for field in fields_to_delete:
                        del json_fields[field]

                    v.serialized_data = json.dumps(j)
                    v.save()
                    print "\t\t [!] Saved"
