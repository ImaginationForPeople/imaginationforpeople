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
from django.db.models import Q
from django.contrib.auth.models import User
from django.template.loader import render_to_string

class UserLookup(object):

    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        return User.objects.filter(Q(username__icontains=q) | 
                                   Q(first_name__icontains=q) | 
                                   Q(last_name__icontains=q) | 
                                   Q(email__icontains=q))

    def format_result(self,user):
        """ the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """
        return render_to_string("member/autocompleteselect_chunk.html", 
                                dictionary={'user' : user})

    def format_item(self,user):
        """ the display of a currently selected object in the area below the search box. html is OK """
        return u"%s %s" % (user.first_name, user.last_name)

    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return User.objects.filter(pk__in=ids).order_by('last_name','first_name')