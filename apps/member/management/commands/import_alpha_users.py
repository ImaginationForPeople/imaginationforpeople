#-- encoding: utf-8 --
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#
from datetime import datetime
from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode

from userena import settings as userena_settings
from userena.models import UserenaSignup

from apps.i4p_base.models import Location
from apps.i4p_base.utils import remove_accents

import csv

class Command(BaseCommand):
    help = "Importation command of the alpha users"
    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='file'),
    )

    def handle(self, *args, **options):
#        User.objects.filter(is_superuser=False).delete()
#        I4pProfile.objects.all().delete()
#        Location.objects.all().delete()

        with open(options.get('file'), 'rb') as file:
            reader = csv.reader(file, delimiter=';')
            reader.next()

            for row in reader:
                full_name, pwd, email, addr, country, zipcode, city, about_me, lon, lat, date_joined = row
                full_name = full_name.split(" ")
                firstname, lastname = full_name[0].title(), " ".join(full_name[1:]).title()
                username = "%s%s" % (firstname, lastname)
                username = remove_accents(username.replace(" ", "").replace("-", ""))

                users = User.objects.filter(username__istartswith=username)
                if users.count() > 0:
                    username = "%s%s" % (username, users.count())

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
                print profile, "[SAVED]"

