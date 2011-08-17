from django.db import models
from django.contrib import admin

from .models import Partner, PartnerPicture

class PartnerPictureInline(admin.TabularInline):
    model = PartnerPicture

class PartnerAdmin(admin.ModelAdmin):
    model = Partner
    inlines = (
        PartnerPictureInline,
        )


admin.site.register(Partner, PartnerAdmin)







