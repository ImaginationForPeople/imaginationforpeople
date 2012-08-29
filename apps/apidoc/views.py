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
"""
Django Views for help
"""

from django.views.generic import TemplateView

from piston.doc import generate_doc

from apps.api.views.project import I4pProjectTranslationHandler

class I4pProjectApiHelp(TemplateView):
    """
    Help page for I4pProjectTranslationHandler
    """
    template_name = 'help/help.html'

    def get_context_data(self, **kwargs):
        context = super(I4pProjectApiHelp, self).get_context_data(**kwargs)

        doc = generate_doc(I4pProjectTranslationHandler)

        context['doc'] = doc

        return context