from userena.forms import AuthenticationForm

from .forms import I4PSignupForm

def member_forms(request):
    """
    Signin and signup forms (for the upper panel)
    """
    additions = {
        'signup_form': I4PSignupForm(),
        'signin_form': AuthenticationForm(),
    }
    return additions













