from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from .models import WorkGroupCMS, WorkGroup
from .utils import get_ml_members

class WorkGroupPlugin(CMSPluginBase):
    model = WorkGroupCMS
    name = _("WorkGroup (un)subscribe button")
    render_template = "workgroup/cms_subscribe_button.html"

    def render(self, context, instance, placeholder):
        workgroup = instance.workgroup
        members = get_ml_members(workgroup)

        context['ml_member_list'] = []
        context['ml_nonmember_list'] = []        
        for member in members:
            try:
                found_member = User.objects.get(email=member[0])
                context['ml_member_list'].append(found_member)
            except User.DoesNotExist:
                context['ml_nonmember_list'].append(User(email=member[0]))


        context['workgroup'] = workgroup

        return context

    def __unicode__(self):
        return u"Workgroup %s" % self.workgroup.slug

plugin_pool.register_plugin(WorkGroupPlugin)
