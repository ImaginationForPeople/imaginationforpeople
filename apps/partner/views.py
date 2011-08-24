from django.views.generic import ListView, DetailView
from django.utils import translation

from .models import Partner

from apps.project_sheet.utils import get_project_translations_from_parents

class PartnerListView(ListView):
    template_name = 'partner/partner_list.html'
    context_object_name = 'partner_list'
    queryset = Partner.objects.all()

class PartnerDetailView(DetailView):
    template_name = 'partner/partner_detail.html'
    context_object_name = 'partner'
    model = Partner

    def get_context_data(self, **kwargs):
        context = super(PartnerDetailView, self).get_context_data(**kwargs)

        partner = context['partner']
        language_code = translation.get_language()
        context['partner_projects'] = get_project_translations_from_parents(parents_qs=partner.projects.all(),
                                                                            language_code=language_code,
                                                                            fallback_language='en',
                                                                            fallback_any=True)

        return context

