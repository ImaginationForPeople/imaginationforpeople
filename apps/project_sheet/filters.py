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
Filter framework
"""
from itertools import chain

from django import forms
from django.db.models import Q
from django.forms.widgets import SelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem, Tag

from apps.project_sheet.models import ProjectMember, Objective

from .models import I4pProjectTranslation, I4pProject
from apps.i4p_base.models import I4P_COUNTRIES
ORDER_CHOICES = (
     ('lte', '<='),
     ('gte', '>=')
)

class FilterSet(object):
    """ 
    Filters container
    """

    def __init__(self, filters):
        self.forms = filters

    def is_valid(self):
        res = True
        for filt in self:
            res &= filt.is_valid()
        return res

    def apply_to(self, queryset, model_class=None):
        qs = queryset
        for filter in self.forms:
            qs = filter.apply_to(qs, model_class)
        return qs

    def __iter__(self):
        return self.forms.__iter__()


class FilterForm(forms.Form):
    """
    Filter base class 
    """
    def apply_to(self, queryset, model_class=None):
        raise NotImplementedError

class ThemesFilterForm(FilterForm):
    """
    Implements a filter on I4pProjectTranslation themes (tags)
    """
    themes = forms.CharField(required=False, label=_("Themes contain"))

    def clean_themes(self):
        data = self.cleaned_data.get('themes', '')
        themes = []
        if data:
            for tag_ids in data.split(','):
                try:
                    tag_id = int(tag_ids)
                    tag = Tag.objects.filter(id=tag_id)
                    themes.extend(tag)
                except ValueError:
                    raise forms.ValidationError("Must be an integer id");
                except Tag.DoesNotExist:
                    raise forms.ValidationError("Unknown theme");
        return themes

    # TODO model_class is useless
    def apply_to(self, queryset, model_class=None):
        qs = queryset
        if qs.query.model == I4pProjectTranslation:
            tags = self.cleaned_data.get("themes")
            if tags:
                qs = TaggedItem.objects.get_union_by_model(queryset, tags)
        return qs

class WithMembersFilterForm(FilterForm):
    """
    Implements a filter on I4pProject including or not members
    """

    with_members = forms.BooleanField(required=False, label=_('With associated leaders'))
    without_members = forms.BooleanField(required=False, label=_('Without associated leaders'))

    def apply_to(self, queryset, model_class=None):
        qs = queryset
        if qs.query.model == I4pProject:
            with_members = self.cleaned_data.get("with_members")
            without_members = self.cleaned_data.get("without_members")
            if with_members != without_members:
                projects_with_members = ProjectMember.objects.values_list('project__id', flat=True).distinct()
                if with_members:
                    qs = qs.filter(id__in=projects_with_members)
                else:
                    qs = qs.exclude(id__in=projects_with_members)
        return qs

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['with_members'].widget.attrs['class'] = 'styled'
        self.fields['without_members'].widget.attrs['class'] = 'styled'

class MyCheckboxSelectMultiple(SelectMultiple):
    """
    Implements custom multi select checkbox widget
    FIXME: find source, maybe djangosnippets.org
    """
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))

            checkbox = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_checkbox = checkbox.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li id="filter_val_%s" title="%s">%s<p>%s</p></li>' % (option_value.lower(),
                                                                                   option_label.title(),
                                                                                   rendered_checkbox,
                                                                                   option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)

class ProjectStatusFilter(FilterForm):
    """
    Implements a filter on I4pProject status
    """
    status = forms.TypedMultipleChoiceField(required=False, coerce=str,
                                            choices=I4pProject.STATUS_CHOICES,
                                            widget=MyCheckboxSelectMultiple)

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
            data = self.cleaned_data.get("status")
            if data :
                q_objects = None
                for val in data:
                    lookup = {"status" : val}
                    if q_objects :
                        q_objects |= Q(**lookup)
                    else :
                        q_objects = Q(**lookup)
                qs = qs.filter(q_objects)
        return qs

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'styled'

class BestOfFilter(FilterForm):
    """
    Implements a filter on I4pProject best of
    """

    best_of = forms.BooleanField(required=False)

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
            val = self.cleaned_data.get("best_of")
            if val :
                qs = qs.filter(best_of=val)
        return qs

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['best_of'].widget.attrs['class'] = 'styled'


class ProjectProgressFilter(FilterForm):
    """
    Implements a filter on I4pProjectTranslation progression
    """

    progress = forms.TypedMultipleChoiceField(required=False, coerce=str,
                                            choices=I4pProjectTranslation.PROGRESS_CHOICES,
                                            widget=MyCheckboxSelectMultiple)

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProjectTranslation:
            data = self.cleaned_data.get("progress")
            if data :
                q_objects = None
                for val in data:
                    lookup = {"completion_progress" : val}
                    if q_objects :
                        q_objects |= Q(**lookup)
                    else :
                        q_objects = Q(**lookup)
                qs = qs.filter(q_objects)
        return qs

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['progress'].widget.attrs['class'] = 'styled'


def current_countries():
    """
    Build the list of countries used in project location 
    """
    result = [("", _("World"))]
    project_countries = I4pProject.objects.exclude(location__country='').\
                                           exclude(location__country__isnull=True).\
                                           distinct().\
                                           order_by('location__country').\
                                           values_list('location__country', flat=True)
    for country in project_countries:
        for code, name in I4P_COUNTRIES:
            if country == code:
                result.append((code, name))
                break
    return result

class ProjectLocationFilter(FilterForm):
    """
    Implements a filter on I4pProject location
    """
    country = forms.ChoiceField(required=False, choices=current_countries())

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
            data = self.cleaned_data.get("country")
            if data:
                q_objects = None
                for val in data:
                    lookup = {"location__country" : val}
                    if q_objects :
                        q_objects |= Q(**lookup)
                    else :
                        q_objects = Q(**lookup)
                qs = qs.filter(q_objects)
        return qs


class ProjectObjectiveFilter(FilterForm):
    """
    Implements a filter on I4pProject objective
    """
    objectives = forms.ModelMultipleChoiceField(required=False, 
                                                queryset=Objective.objects.all())

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
            data = self.cleaned_data.get("objectives")
            if data:
                qs = qs.filter(objectives__in=[d.id for d in data])
        return qs

class NameBaselineFilter(FilterForm):
    """
    Simulates a full-text search in either the baseline or the title.
    """
    text = forms.CharField(max_length=100, required=False)

    def apply_to(self, queryset, model_class):
        if model_class == I4pProjectTranslation:
            text = self.cleaned_data.get("text")
            filters = Q(title__icontains=text) | Q(baseline__icontains=text)
            queryset = queryset.filter(filters)

        return queryset
