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
Django Admin for members
"""
from django.contrib import admin
from .models import I4pProfile

class I4pProfileAdmin(admin.ModelAdmin):
    model = I4pProfile

    list_display = ('user', 'language',)

    def make_mailing_list(self, request, queryset):
        from emencia.django.newsletter.models import Contact
        from emencia.django.newsletter.models import MailingList

        subscribers = []
        for profile in queryset:
          contact, created = Contact.objects.get_or_create(email=profile.user.email,
                                                           defaults={'first_name': profile.user.first_name,
                                                                     'last_name': profile.user.last_name,
                                                                     'content_object': profile})
          subscribers.append(contact)

        new_mailing = MailingList(name='New mailing list',
                                  description='New mailing list created from admin/profile')
        new_mailing.save()
        new_mailing.subscribers.add(*subscribers)
        new_mailing.save()
        self.message_user(request, '%s succesfully created.' % new_mailing)
    make_mailing_list.short_description = 'Create a mailing list'

    actions = ['make_mailing_list',]

admin.site.unregister(I4pProfile)
admin.site.register(I4pProfile, I4pProfileAdmin)
