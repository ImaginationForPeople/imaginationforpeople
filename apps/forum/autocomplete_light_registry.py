import autocomplete_light

from askbot.models.question import Thread

class AutocompleteThread(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ('title','tagnames')
    choices = Thread.objects.all()

#    def choices_for_request(self):
#        q = self.request.GET.get('q', '')
#        project_translations = I4pProjectTranslation.objects.filter(title__icontains=q)
#        return [project_translation.project for project_translation in project_translations]

autocomplete_light.register(Thread, AutocompleteThread) 

        


