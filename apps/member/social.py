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
import StringIO
import sys
from urllib2 import urlopen

from django.conf import settings
from django.core.files import File
from django.utils import simplejson

from easy_thumbnails.files import get_thumbnailer
from apps.i4p_base.models import Location, I4P_COUNTRIES


def fetch_country(profile, response):
    try:
        location_name = response['location']['name']
        city, country = [s.strip() for s in location_name.split(",")]
        profile.address = city
        for country_code, i18n_proxy in I4P_COUNTRIES:
            # Need to coerce Django i18n proxy into uncidoe
            country_name = unicode(i18n_proxy)
            if country_name == country:
                profile.country = country_code
                break
        location_url = "http://graph.facebook.com/%s" % response['location']['id']
        location_request = urlopen(location_url)
        location_data = simplejson.loads(location_request.read())['location']
        location = Location(lat=location_data['latitude'],
                            lon=location_data['longitude'],
                            address=city,
                            country=profile.country)
        profile.location = location
    except KeyError, e:
        # Don't propagate errors caused by missing data
        print >> sys.stderr, '***', e


def fetch_facebook_details(profile, response):
    """
    Fetch facebook picture and store it with the user's profile
    """
    try:
        profile.website = response.get('website')
        profile.facebook = response.get('link')
        fetch_country(profile, response)

        # Get profile picture
        #
        # easy_thumbnails requires a django File object which itself needs a
        # file-like object so we do a little dance with StringIO to make it work.
        photo_url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        photo = urlopen(photo_url)
        photo_io = StringIO.StringIO()
        photo_io.write(photo.read())
        thumbnailer = get_thumbnailer(File(photo_io),
                relative_name=("%s%s-facebook-picture" %
                    (settings.USERENA_MUGSHOT_PATH, profile.user.username)))
        thumb = thumbnailer.generate_thumbnail({'size': (200, 200)})
        profile.mugshot = thumb

        profile.save() 
    except Exception, e:
        # An exception while fetching user details from facebook shouldn't crash
        # the registraion process
        print >> sys.stderr, '***', e
