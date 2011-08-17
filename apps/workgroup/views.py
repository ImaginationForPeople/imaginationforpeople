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


class WorkGroupListView(ListView):
    template_name = 'workgroup/workgroup_list.html'
    context_object_name = 'workgroup_list'
    queryset = WorkGroup.objects.all()

class WorkGroupDetailView(DetailView):
    template_name = 'workgroup/workgroup_detail.html'
    context_object_name = 'workgroup'
    model = WorkGroup

    def _get_ml_members(self, workgroup):
        cache_key = '%s-ml-members' % workgroup.slug
        res = cache.get(cache_key, None)
        print "cache is", res
        if not res:
            res = workgroup.mailing_list.get_all_members()
            cache.set(cache_key, res, 3600)

        return res

    def get_context_data(self, **kwargs):
        """
        Adds the member of the associated ML if there's one
        """
        context = super(WorkGroupDetailView, self).get_context_data(**kwargs)
        
        workgroup = context['workgroup']
        if workgroup.mailing_list:
            context['ml_member_list'] = []
            context['ml_nonmember_list'] = []
            members = self._get_ml_members(workgroup) # workgroup.mailing_list.get_all_members()
            
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
    def post(self, request, workgroup_slug):
        workgroup = get_object_or_404(WorkGroup, slug=workgroup_slug)
        user = request.user

        # Force cache regeneration
        cache_key = '%s-ml-members' % workgroup.slug
        cache.delete(cache_key)


        if workgroup.mailing_list:
            ml = workgroup.mailing_list
            try:
                ml.subscribe(user.email, user.first_name, user.last_name)
                
                messages.success(request, _(u"You have been successfully subscribed to the"
                                            u"%(workgroup_name)s mailing list"
                                            u" (%(user_email)s)" % {'workgroup_name': workgroup.name,
                                                                    'user_email': user.email}
                                            )
                                 )
            except Exception, e:
                messages.error(request, _(u"You couldn't be subscribed to this workgroup:%s" % unicode(e.message, encoding=ml.encoding)))

        return redirect('workgroup-detail', workgroup.slug)


class UnsubscribeView(View):
    """
    Subscribe a user to the mailing list
    """
    @method_decorator(login_required)
    def post(self, request, workgroup_slug):
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

        return redirect('workgroup-detail', workgroup.slug)
            
        
