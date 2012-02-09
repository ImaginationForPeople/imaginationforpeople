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
from urllib2 import urlopen
import urlparse

from django.conf import settings
from django.core.files import File
from django.utils import simplejson

from easy_thumbnails.files import get_thumbnailer
import oauth2
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.google import GoogleOAuth2Backend
from social_auth.backends.contrib.linkedin import LinkedinBackend

from apps.i4p_base.models import Location, I4P_COUNTRIES
from .utils import fix_username


class DataAdapter(object):
    """
    Mixin class hosting methods useful to different social data adapters.
    """

    def __init__(self, profile, response):
        self.profile = profile
        self.response = response

    def fetch_picture(self):
        """
        Get profile picture from a URL

        easy_thumbnails requires a django File object which itself needs a
        file-like object so we do a little dance with StringIO to make it work.
        """
        photo = urlopen(self.picture_url)
        photo_io = StringIO.StringIO()
        photo_io.write(photo.read())
        thumbnailer = get_thumbnailer(File(photo_io),
                relative_name=("%s%s-picture" % (settings.USERENA_MUGSHOT_PATH,
                                                 self.profile.user.username)))
        thumb = thumbnailer.generate_thumbnail({'size': (200, 200)})
        self.profile.mugshot = thumb

    def set_twitter_url(self, screen_name):
        """
        Return twitter URL from screen name
        """
        twitter_url = 'http://twitter.com/' + screen_name
        self.profile.twitter = twitter_url

    def make_username_from(self, first_name, last_name):
        """
        Set a username from profile first name and last name
        """
        default_username = self.profile.user.username
        fancy_username = first_name.capitalize() + last_name.capitalize()
        if default_username.startswith(fancy_username.lower()):
            # If default username already starts with a lowercase version of the
            # username based on first name and last name, we replace it by its
            # camel case counterpart. Example: if Google email is
            # john.smith@gmail.com, default username could be johnsmith2 if
            # there's already a JohnSmith, then we want the new fancy username
            # to be JohnSmith2
            self.profile.user.username = default_username.replace(
                        fancy_username.lower(), fancy_username)
        else:
            self.profile.user.username = fix_username(fancy_username)


class FacebookDataAdapter(DataAdapter):
    """
    Populates user profile attributes using data fetched from Facebook.

    Tries to populate these fields:
     - first_name
     - last_name
     - email
     - country
     - location
     - website
     - facebook (profile URL)
     - mugshot (profile picture)
    """

    def fetch_profile_data(self):
        """
        Get profile data from authentication response and assign it to user
        profile
        """
        print self.response
        self.profile.user.first_name = self.response.get('first_name', '')
        self.profile.user.last_name = self.response.get('last_name', '')
        self.make_username_from(self.profile.user.first_name,
                                self.profile.user.last_name)

        self.profile.website = self.response.get('website', '')
        self.profile.facebook = self.response.get('link', '')
        self.fetch_country()
        self.fetch_picture()

    @property
    def picture_url(self):
        template = "http://graph.facebook.com/%s/picture?type=large"
        return template % self.response['id']

    def fetch_country(self):
        try:
            location_name = self.response['location']['name']
            city, country = [s.strip() for s in location_name.split(",")]
            self.profile.address = city
            for country_code, i18n_proxy in I4P_COUNTRIES:
                # Need to coerce Django i18n proxy into unicode
                country_name = unicode(i18n_proxy)
                if country_name == country:
                    self.profile.country = country_code
                    break
            location_url = "http://graph.facebook.com/%s" % self.response['location']['id']
            location_request = urlopen(location_url)
            location_response = simplejson.loads(location_request.read())
            location_data = location_response['location']
            location = Location(lat=location_data['latitude'],
                                lon=location_data['longitude'],
                                address=city,
                                country=self.profile.country)
            self.profile.location = location
        except KeyError:
            # Don't propagate errors caused by missing data
            pass


class TwitterDataAdapter(DataAdapter):
    """
    Populates user profile attributes using data fetched from Twitter.

    Tries to populate these fields:
     - first_name (Twitter only has a "name" field, django-social-auth uses
       the content of that field to populate user.first_name)
     - website
     - location
     - twitter (twitter profile URL)
     - mugshot (profile picture)

    Email address is NOT available via Twitter API.
    """

    def fetch_profile_data(self):
        """
        Get profile data from authentication response and assign it to user
        profile

        Twitter API doesn't currently give access to location or email address
        """
        self.set_twitter_url(self.response.get('screen_name'))
        self.fetch_picture()
        self.profile.website = self.response.get('url', '')
        location = Location(address=self.response.get('location'))
        self.profile.location = location

    @property
    def picture_url(self):
        template = "https://api.twitter.com/1/users/profile_image?screen_name=%s&size=bigger"
        return template % self.response['screen_name']


class GoogleDataAdapter(DataAdapter):
    """
    Populates user profile attributes using data fetched from Twitter.

    Tries to populate these fields:
     - first_name
     - last_name
     - email
     - mugshot (profile picture)
     - gender
    """

    def __init__(self, profile, response):
        DataAdapter.__init__(self, profile, response)
        token = self.response['access_token']
        profile_url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=' + token
        profile_json = urlopen(profile_url).read()
        self.user_info = simplejson.loads(profile_json)

    def fetch_profile_data(self):
        self.profile.user.first_name = self.user_info.get('given_name', '')
        self.profile.user.last_name = self.user_info.get('family_name', '')
        self.make_username_from(self.profile.user.first_name,
                                self.profile.user.last_name)
        if self.user_info.get('gender') == 'male':
            self.profile.gender = 'M'
        elif self.user_info.get('gender') == 'female':
            self.profile.gender = 'F'
        self.fetch_picture()

    @property
    def picture_url(self):
        return self.user_info['picture']


class LinkedinDataAdapter(DataAdapter):
    """
    Populates user profile attributes using data fetched from Twitter.

    Tries to populate these fields:
     - first_name
     - last_name
     - country
     - location
     - mugshot (profile picture)
     - website (first resource URLs)
     - twitter (first twitter account registered with LinkedIn)
     - linked (profile URL)

    Email address is NOT available via LinkedIn API.
    """

    def __init__(self, profile, response):
        DataAdapter.__init__(self, profile, response)

        # OAuth dance documented at
        # https://developer.linkedin.com/documents/quick-start-guide
        consumer = oauth2.Consumer(settings.LINKEDIN_CONSUMER_KEY,
                settings.LINKEDIN_CONSUMER_SECRET)
        access_token = dict(urlparse.parse_qsl(self.response['access_token']))
        token = oauth2.Token(
                    key=access_token['oauth_token'],
                    secret=access_token['oauth_token_secret'])
        client = oauth2.Client(consumer, token)

        # Simple profile call. Field selectors reference:
        # https://developer.linkedin.com/documents/profile-fields
        base_url = "http://api.linkedin.com/v1/people/~"
        fields = "(public-profile-url,picture-url,member-url-resources:(url),"
        fields += "twitter-accounts,location:(name,country:(code)))"
        url = ":".join([base_url, fields])
        _, content = client.request(url, 'GET',
                                       headers={"x-li-format": 'json'})
        self.user_info = simplejson.loads(content)

    def fetch_profile_data(self):
        """
        Fetch profile data from LinkedIn
        """
        country_code = self.user_info['location']['country']['code'].upper()
        self.profile.country = country_code

        location_name = self.user_info['location']['name']
        location = Location(address=location_name, country=country_code)
        self.profile.location = location

        self.profile.linkedin = self.user_info['publicProfileUrl']

        # Pick first URL resource as user's website
        websites = self.user_info['memberUrlResources']
        if websites['_total'] > 0:
            self.profile.website = websites['values'][0]['url']

        # Try to populate twitter account
        twitters = self.user_info['twitterAccounts']
        if twitters['_total'] > 0:
            screen_name = twitters['values'][0]['providerAccountName']
            self.set_twitter_url(screen_name)

        self.fetch_picture()

    @property
    def picture_url(self):
        return self.user_info['pictureUrl']


DATA_ADAPTERS = {
    FacebookBackend: FacebookDataAdapter,
    TwitterBackend: TwitterDataAdapter,
    GoogleOAuth2Backend: GoogleDataAdapter,
    LinkedinBackend: LinkedinDataAdapter,
}


def fetch_profile_data(backend, profile, response):
    """
    Get profile data from response returned by social backend and use if to
    populate user profile.
    """
    if backend in DATA_ADAPTERS:
        adapter_class = DATA_ADAPTERS[backend]
        try:
            adapter = adapter_class(profile, response)
            adapter.fetch_profile_data()
        except Exception:
            # Errors while fetching profile data shouldn't be fatal.
            # Automatically populating user's profile is a nice thing to do, but
            # we don't want it to stop the registration process if it doesn't
            # work.
            pass

        profile.save()
