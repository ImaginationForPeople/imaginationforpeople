from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import GenericPage

def manifesto(request):

    manifesto_copy = GenericPage.objects.get(title='manifeste')

    # render the response
    return render_to_response('default.html', 
                              {'manifesto_copy':manifesto_copy}, 
                              context_instance=RequestContext(request))
