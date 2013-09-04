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

from honeypot.middleware import HoneypotMiddleware

class I4pHoneypotMiddleware(HoneypotMiddleware):
    '''
    I4P specific implementation of HoneypotMiddleware
    to permit POST requests to API
    '''
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.path.startswith("/api"):
            return None
        return super(HoneypotMiddleware, self).process_view(request, callback, callback_args, callback_kwargs)
        