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
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import ListView, DetailView
from django.views.generic import View

from .models import WorkGroup
from .utils import get_ml_members

class WorkGroupListView(ListView):
    template_name = 'workgroup/workgroup_list.html'
    context_object_name = 'workgroup_list'
    queryset = WorkGroup.objects.all()

class WorkGroupDetailView(DetailView):
    template_name = 'workgroup/workgroup_detail.html'
    context_object_name = 'workgroup'
    model = WorkGroup

    def get_context_data(self, **kwargs):
        """
        Adds the member of the associated ML if there's one
        """
        context = super(WorkGroupDetailView, self).get_context_data(**kwargs)
        
        workgroup = context['workgroup']
        if workgroup.mailing_list:
            context['ml_member_list'] = []
            context['ml_nonmember_list'] = []
            members = get_ml_members(workgroup) # workgroup.mailing_list.get_all_members()
            
            for member in members:
                try:
                    found_member = User.objects.get(email=member[0])
                    context['ml_member_list'].append(found_member)
                except User.DoesNotExist:
                    context['ml_nonmember_list'].append(User(email=member[0]))

        return context



class SubscribeView(View):
    """
    Subscribe a user to the mailing list
    """
    @method_decorator(login_required)
    def get(self, request, workgroup_slug):
        workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)
        user = request.user

        # Force cache regeneration
        cache_key = '%s-ml-members' % workgroup.slug
        cache.delete(cache_key)

        if workgroup.mailing_list:
            ml = workgroup.mailing_list
            try:
                ml.subscribe(user.email,
                             user.first_name,
                             user.last_name,
                             send_welcome_msg=True)

                messages.success(request, _(u"You have been successfully subscribed to the"
                                            u"%(workgroup_name)s mailing list"
                                            u" (%(user_email)s)" % {'workgroup_name': workgroup.name,
                                                                    'user_email': user.email}
                                            )
                                 )
            except Exception, e:
                messages.error(request, _(u"You couldn't be subscribed to this workgroup:%s" % unicode(e.message, encoding=ml.encoding)))

        next_url = request.GET.get('next_url', None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect('workgroup-detail', workgroup.slug)


class UnsubscribeView(View):
    """
    Subscribe a user to the mailing list
    """
    @method_decorator(login_required)
    def get(self, request, workgroup_slug):
        workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)
        user = request.user

        # Force cache regeneration
        cache_key = '%s-ml-members' % workgroup.slug
        cache.delete(cache_key)

        if workgroup.mailing_list:
            ml = workgroup.mailing_list
            try:
                ml.unsubscribe(user.email)

                messages.success(request, _(u"You have been successfully unsubscribed from the"
                                            u"%(workgroup_name)s mailing list"
                                            u" (%(user_email)s)" % {'workgroup_name': workgroup.name,
                                                                    'user_email': user.email}
                                            )
                                 )
            except Exception, e:
                messages.error(request, _(u"You couldn't be unsubscribed from this workgroup:%s" % e.message))

        next_url = request.GET.get('next_url', None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect('workgroup-detail', workgroup.slug)

            
        
