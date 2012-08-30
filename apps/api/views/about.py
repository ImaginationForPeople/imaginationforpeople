# -*- encoding: utf-8 -*-
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

from django.conf import settings

from piston.handler import BaseHandler
from piston.utils import throttle

class AboutHandler(BaseHandler):
    """
    Get informations about the API
    """
    allowed_methods = ('GET',)
    
    @throttle(settings.API_THROTTLE_REQUEST_COUNT, settings.API_THROTTLE_REQUEST_TIMEFRAME)
    def read(self, request):
        """Display informations about the API
        
        Returns a JSON object with the following attributes:
        * version: current version of the API
        * throttle_count: maximum number of requests per time unit (see throttle_timeframe)
        * throttle_timeframe: time unit (in seconds)
        """
        
        about = {
            "version": 1,
            "throttle_count": settings.API_THROTTLE_REQUEST_COUNT,
            "throttle_timeframe": settings.API_THROTTLE_REQUEST_TIMEFRAME,
        }
        
        return about
