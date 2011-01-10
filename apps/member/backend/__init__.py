from registration.backends.default import DefaultBackend
from django.contrib.auth import login, authenticate, get_backends

class I4pRegistrationBackend(DefaultBackend):
    def post_activation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        account activation.
        
        """
        backend = get_backends()[0]
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, user)
        return ('registration_activation_complete', (), {})