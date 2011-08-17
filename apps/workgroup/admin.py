from django.db import models
from django.contrib import admin

from django_mailman.models import List

from .models import WorkGroup

class MailingListAdmin(admin.ModelAdmin):
    model = List

class WorkGroupAdmin(admin.ModelAdmin):
    model = WorkGroup


admin.site.register(WorkGroup, WorkGroupAdmin)
admin.site.register(List, MailingListAdmin)
