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
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.contrib.linkedin import LinkedinBackend

from apps.i4p_base.models import Location, I4P_COUNTRIES


class DataAdapter(object):

    def __init__(self, profile, response):
        self.profile = profile
        self.response = response

    def fetch_picture(self):
        """
        Get profile picture from a URL
        
        easy_thumbnails requires a django File object which itself needs a
        file-like object so we do a little dance with StringIO to make it work.
        """
        photo = urlopen(self.photo_url)
        photo_io = StringIO.StringIO()
        photo_io.write(photo.read())
        thumbnailer = get_thumbnailer(File(photo_io),
                relative_name=("%s%s-picture" %
                    (settings.USERENA_MUGSHOT_PATH, self.profile.user.username)))
        thumb = thumbnailer.generate_thumbnail({'size': (200, 200)})
        self.profile.mugshot = thumb


class FacebookDataAdapter(DataAdapter):

    def fetch_profile_data(self):
        """
        Get profile data from authentication response and assign it to user
        profile
        """
        self.profile.website = self.response.get('website')
        self.profile.facebook = self.response.get('link')
        self.fetch_country()
        self.fetch_picture()

    @property
    def photo_url(self):
        template = "http://graph.facebook.com/%s/picture?type=large"
        return template % self.response['id']

    def fetch_country(self):
        try:
            location_name = self.response['location']['name']
            city, country = [s.strip() for s in location_name.split(",")]
            self.profile.address = city
            for country_code, i18n_proxy in I4P_COUNTRIES:
                # Need to coerce Django i18n proxy into uncidoe
                country_name = unicode(i18n_proxy)
                if country_name == country:
                    self.profile.country = country_code
                    break
            location_url = "http://graph.facebook.com/%s" % self.response['location']['id']
            location_request = urlopen(location_url)
            location_data = simplejson.loads(location_request.read())['location']
            location = Location(lat=location_data['latitude'],
                                lon=location_data['longitude'],
                                address=city,
                                country=self.profile.country)
            self.profile.location = location
        except KeyError, e:
            # Don't propagate errors caused by missing data
            print >> sys.stderr, '***', e


class TwitterDataAdapter(DataAdapter):

    def fetch_profile_data(self):
        """
        Get profile data from authentication response and assign it to user
        profile

        Twitter API doesn't currently give access to location or email address
        """
        self.profile.website = self.response.get('url')
        self.profile.twitter = 'http://twitter.com/' + self.response.get('screen_name')
        self.fetch_picture()

    @property 
    def photo_url(self):
        template = "https://api.twitter.com/1/users/profile_image?screen_name=%s&size=bigger"
        return template % self.response['screen_name']



def fetch_profile_data(backend, profile, response):
    """
    Get profile data from response returned by the backend and assign to user
    profile
    """
    adapters = {
            FacebookBackend: FacebookDataAdapter,
            TwitterBackend: TwitterDataAdapter,
            }
    adapter_class = adapters[backend]
    adapter = adapter_class(profile, response)

    try:
        adapter.fetch_profile_data()
    except Exception, e:
        # Errors while fetching profile data shouldn't be fatal.
        # Automatically populating user's profile is a nice thing to do, but we
        # don't want it to stop the registration process if it doesn't work.
        print >> sys.stderr, '***', e
        raise

    profile.save()
