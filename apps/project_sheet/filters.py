from django import forms
from tagging.models import TaggedItem, Tag
from .models import I4pProjectTranslation, I4pProject
from django.utils.translation import ugettext as _

ORDER_CHOICES = (
     ('lte', '<='),
     ('gte', '>=')
)

class FilterSet(object):

    def __init__(self, filterForm, data=None):
        self.is_bound = data and True
        self.order_form = forms.Form()
        self.filter_forms = []
        idx = 1
        for f in filterForm:
            if data :
                self.add_filter_form(f(data, prefix="filter%s" % idx))
            else:
                self.add_filter_form(f(prefix="filter%s" % idx))
            idx += 1

    def add_filter_form(self, aForm):
        if isinstance(aForm, FilterForm):
            self.filter_forms.append(aForm)
        else:
            raise TypeError()

    def is_valid(self):
        res = True
        if self.is_bound:
            for f in self:
                res &= f.is_valid()
        else:
            res = False
        return res

    def apply_to(self, queryset):
        qs = queryset
        for f in self.filter_forms:
            qs = f.apply_to(qs)
        return qs

    def __iter__(self):
        return self.filter_forms.__iter__()


class FilterForm(forms.Form):
    def apply_to(self, queryset):
        raise NotImplementedError

class TitleFilterForm(FilterForm):
    title = forms.CharField(max_length=80,
                            required=False,
                            label=_("Title must contains"))

    def apply_to(self, queryset):
        qs = queryset
        title = self.cleaned_data.get("title")
        if title:
            qs = qs.filter(**{"title__icontains":title})
        return qs

class OjectiveFilterForm(FilterForm):
    objective = forms.ChoiceField(choices=I4pProject.OBJECTIVE_CHOICES,
                                  required=False,
                                  label=_("Objective is"))

    def apply_to(self, queryset):
        qs = queryset
        objective = self.cleaned_data.get("objective")
        if objective:
            qs = qs.filter(**{"project__objective":objective})
        return qs

class ThemesFilterForm(FilterForm):
    themes = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(id__in=[t.id for t in Tag.objects.usage_for_model(I4pProjectTranslation)]),
                                            required=False,
                                            label=_("Themes contain"))

    def apply_to(self, queryset):
        tags = self.cleaned_data.get("themes")
        if tags:
            return TaggedItem.objects.get_intersection_by_model(queryset, tags)

        return queryset

class CreationFilterForm(FilterForm):
    created_order = forms.ChoiceField(choices=ORDER_CHOICES,
                                      label=_("Created "))
    created = forms.DateField(required=False,
                              label="",
                              input_formats=['%Y-%m-%d',
                                             '%m/%d/%Y',
                                             '%m/%d/%y'])

    def apply_to(self, queryset):
        qs = queryset
        created = self.cleaned_data.get("created")
        if created:
            created_order = self.cleaned_data.get("created_order")
            qs = qs.filter(**{"project__created__%s" % created_order :created})
        return qs
