from django.views.generic import ListView, DetailView

from .models import Partner

class PartnerListView(ListView):
    template_name = 'partner/partner_list.html'
    context_object_name = 'partner_list'
    queryset = Partner.objects.all()

class PartnerDetailView(DetailView):
    template_name = 'partner/partner_detail.html'
    context_object_name = 'partner'
    model = Partner

