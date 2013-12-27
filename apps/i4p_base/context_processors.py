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

from haystack.forms import SearchForm
from site_settings import *

def search_form(request):
    additions = {
        'search_form': SearchForm(),
    }
    return additions

def settings(request):
    additions = {}
    
    try:
        additions['ADDTHIS_USERNAME'] = ADDTHIS_USERNAME
    except NameError:
        additions['ADDTHIS_USERNAME'] = None

    try:
        additions['GOOGLE_ANALYTICS_ACCOUNT'] = GOOGLE_ANALYTICS_ACCOUNT
    except NameError:
        additions['GOOGLE_ANALYTICS_ACCOUNT'] = None
        
    return additions











