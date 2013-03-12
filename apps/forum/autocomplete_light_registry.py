import autocomplete_light

from askbot.models.question import Thread

class AutocompleteThread(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ('title', 'tagnames')
    choices = Thread.objects.all()
 
autocomplete_light.register(Thread, AutocompleteThread) 

        


