from django import forms
from .models import I4pProject
from django.forms.models import modelform_factory

I4pProjectTitleFieldForm = modelform_factory(I4pProject, fields=('title',))
I4pProjectBaselineFieldForm = modelform_factory(I4pProject, fields=('baseline',))
I4pProjectAboutFieldForm = modelform_factory(I4pProject, fields=('about_section',))
I4pProjectUniquenessFieldForm = modelform_factory(I4pProject, fields=('uniqueness_section',))
I4pProjectValueFieldForm = modelform_factory(I4pProject, fields=('value_section',))
I4pProjectScalabilityFieldForm = modelform_factory(I4pProject, fields=('scalability_section',))