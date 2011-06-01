from django import forms
from tagging.models import TaggedItem, Tag
from .models import I4pProjectTranslation, I4pProject
from django.utils.translation import ugettext as _
from django.db.models import Q
from apps.project_sheet.models import ProjectMember
from django.db.models.query import QuerySet
from django.forms.widgets import SelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from itertools import chain
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from django_countries.countries import COUNTRIES

ORDER_CHOICES = (
     ('lte', '<='),
     ('gte', '>=')
)

class FilterSet(object):

    def __init__(self, filter_or_orderer_forms):
        self.forms = filter_or_orderer_forms.values()


    def is_valid(self):
        res = True
        for f in self:
            res &= f.is_valid()
        return res

    def apply_to(self, queryset, model_class):
        qs = queryset
        for f in self.forms:
            qs = f.apply_to(qs, model_class)
        return qs

    def __iter__(self):
        return self.forms.__iter__()


class FilterForm(forms.Form):
    pass

class ThemesFilterForm(FilterForm):
    themes = forms.CharField(required=False, label=_("Themes contain"))

    def get_tags(self):
        data = self.cleaned_data
        if data.get("themes"):
            tag_ids = [int(x) for x in data.get("themes").split(',')]
            return Tag.objects.filter(id__in=tag_ids)
        return []

    def apply_to(self, queryset, model_class):
        if model_class == I4pProjectTranslation:
            tags = self.get_tags()
            if tags:
                return TaggedItem.objects.get_union_by_model(queryset, tags)

        return queryset

class WithMembersFilterForm(FilterForm):
    with_members = forms.BooleanField(required=False, label=_('With associated leaders'))
    without_members = forms.BooleanField(required=False, label=_('Without associated leaders'))

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
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

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li id="filter_val_%s" title="%s">%s<p>%s</p></li>' % (option_value.lower(),
                                                                                   option_label.title(),
                                                                                   rendered_cb,
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
    status = forms.TypedMultipleChoiceField(required=False, coerce=str,
                                            choices=I4pProject.STATUS_CHOICES,
                                            widget=MyCheckboxSelectMultiple)

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
            data = self.cleaned_data.get("status")
            if data :
                q = None
                for val in data:
                    lookup = {"status" : val}
                    if q :
                        q |= Q(**lookup)
                    else :
                        q = Q(**lookup)
                qs = qs.filter(q)
        return qs

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'styled'

class BestOfFilter(FilterForm):
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
    progress = forms.TypedMultipleChoiceField(required=False, coerce=str,
                                            choices=I4pProjectTranslation.PROGRESS_CHOICES,
                                            widget=MyCheckboxSelectMultiple)

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProjectTranslation:
            data = self.cleaned_data.get("progress")
            if data :
                q = None
                for val in data:
                    lookup = {"completion_progress" : val}
                    if q :
                        q |= Q(**lookup)
                    else :
                        q = Q(**lookup)
                qs = qs.filter(q)
        return qs

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['progress'].widget.attrs['class'] = 'styled'


def current_countries():
    result = []
    project_countries = I4pProject.objects.exclude(location__country='').exclude(location__country__isnull=True).distinct().order_by('location__country').values_list('location__country', flat=True)
    for country in project_countries:
        for code, name in COUNTRIES:
            if country == code:
                result.append((code, name))
                break
    return result

class ProjectLocationFilter(FilterForm):
    country = forms.MultipleChoiceField(required=False,
                                        choices=current_countries())

    def apply_to(self, queryset, model_class):
        qs = queryset
        if model_class == I4pProject:
            data = self.cleaned_data.get("country")
            if data :
                q = None
                for val in data:
                    lookup = {"location__country" : val}
                    if q :
                        q |= Q(**lookup)
                    else :
                        q = Q(**lookup)
                qs = qs.filter(q)
        return qs


class NameBaselineFilter(FilterForm):
    """
    Simulates a full-text search in either the baseline or the title.
    """
    text = forms.CharField(max_length=100, required=False)

    def apply_to(self, queryset, model_class):
        if model_class == I4pProjectTranslation:
            text = self.cleaned_data.get("text")
            filters = Q(title__contains=text) | Q(baseline__contains=text)
            queryset = queryset.filter(filters)

        return queryset
