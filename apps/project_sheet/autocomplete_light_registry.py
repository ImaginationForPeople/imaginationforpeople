import autocomplete_light

from .models import I4pProject, I4pProjectTranslation

class AutocompleteI4pProject(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ('title',)
    choices = I4pProject.objects.all()

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        project_translations = I4pProjectTranslation.objects.filter(title__icontains=q)
        return [project_translation.project for project_translation in project_translations]

autocomplete_light.register(I4pProject, AutocompleteI4pProject) 

        


