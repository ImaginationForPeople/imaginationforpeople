from django.contrib.auth.models import User

import autocomplete_light

class AutocompleteUser(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ('username', 'first_name', 'last_name')

autocomplete_light.register(User, AutocompleteUser) 
        

