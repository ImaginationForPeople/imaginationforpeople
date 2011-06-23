from django.core.management.base import BaseCommand

import csv
from optparse import make_option
from django.contrib.auth.models import User
import unicodedata
from datetime import datetime
from apps.member.models import I4pProfile
from apps.i4p_base.models import Location
from userena.models import UserenaSignup
from userena import settings as userena_settings
from django.utils.encoding import smart_unicode

def remove_accents(str):
    nkfd_form = unicodedata.normalize('NFKD', str.decode("utf-8"))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


class Command(BaseCommand):
    help = "Importation command of the alpha users"
    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='file'),
    )

    def handle(self, *args, **options):
        User.objects.filter(is_superuser=False).delete()
        I4pProfile.objects.all().delete()
        Location.objects.all().delete()

        with open(options.get('file'), 'rb') as f:
            reader = csv.reader(f, delimiter=';')
            reader.next()

            for row in reader:
                full_name, pwd, email, addr, country, zipcode, city, about_me, lon, lat, date_joined = row
                full_name = full_name.split(" ")
                firstname, lastname = full_name[0].title(), " ".join(full_name[1:]).title()
                username = "%s%s" % (firstname, lastname)
                username = remove_accents(username.replace(" ", "").replace("-", ""))
                print username, firstname, lastname

                if User.objects.filter(username=username).count() == 0:
                    user = UserenaSignup.objects.create_inactive_user(username, email, "changeme", send_email=False)
                    userena = UserenaSignup.objects.get(user__username=username)

                    assert user.id == userena.user.id

                    userena.activation_key = userena_settings.USERENA_ACTIVATED
                    user = userena.user
                    user.is_active = True
                    userena.save()

                    user.first_name = firstname
                    user.last_name = lastname
                    user.date_joined = datetime.strptime(date_joined, "%Y-%m-%d %H:%M:%S")
                    user.email = email
                    user.password = "md5$$%s" % pwd
                    user.save()

                    full_addr = []
                    addr = addr.strip()
                    if addr:
                        full_addr.append(addr)
                    if zipcode:
                        full_addr.append(zipcode)
                    if city:
                        full_addr.append(city)
                    if full_addr:
                        addr = ",".join(full_addr)

                    lon = lon.strip() or "0.0"
                    lat = lat.strip() or "0.0"

                    location = Location.objects.create(lon=float(lon),
                                                       lat=float(lat),
                                                       country=country.upper(),
                                                       address=addr)
                    profile = user.get_profile()

                    profile.about = about_me
                    profile.address = smart_unicode(addr)
                    profile.country = country.upper()
                    profile.location = location
                    profile.save()

