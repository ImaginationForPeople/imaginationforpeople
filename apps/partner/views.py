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
        context['partner_projects'] = partner.projects.all()

        return context

