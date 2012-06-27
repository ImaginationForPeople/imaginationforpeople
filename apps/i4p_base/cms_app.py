from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class I4PBaseApp(CMSApp):
    name = _("I4PBase App")
    urls = ["apps.i4p_base.urls"]

apphook_pool.register(I4PBaseApp)