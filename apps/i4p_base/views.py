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
# -*- coding: utf-8 -*-
from datetime import datetime
import random

from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import translation

from apps.project_sheet.models import I4pProject
from apps.project_sheet.utils import get_project_translations_from_parents

def homepage(request):
    """
    I4P Homepage
    """
    project_sheets = I4pProject.on_site.filter(best_of=True).order_by('?')[:14]
    project_translations = get_project_translations_from_parents(project_sheets,
                                                                 language_code=translation.get_language()
                                                                 )

    latest_members = list(User.objects.filter(is_active=True).order_by('-date_joined')[:7])
    random.shuffle(latest_members)

    
    data = request.GET

    context = {'project_sheets': project_sheets,
               'project_translations': project_translations,
               'last_members': latest_members,
               'about_tab_selected' : True}

    return render_to_response(template_name='pages/homepage.html',
                              dictionary=context,
                              context_instance=RequestContext(request)
                              )


from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView

from .models import VersionActivity

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from urlparse import urlsplit

class VersionActivityCheckView(RedirectView):
    """
    Approves a Version Activity (an admin reviewed it).
    """
    permanent = False

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(VersionActivityCheckView, self).dispatch(*args, **kwargs)
        
    def get_redirect_url(self, pk):
        activity_revision = get_object_or_404(VersionActivity, pk=pk)

        activity_revision.checked_by = self.request.user
        activity_revision.checked_on = datetime.now()
        activity_revision.save()
        
        referer = self.request.META.get('HTTP_REFERER', None)
        if referer:
            try:
                redirect_to = urlsplit(referer, 'http', False)[2]
            except IndexError:
                pass
                
            return redirect_to
