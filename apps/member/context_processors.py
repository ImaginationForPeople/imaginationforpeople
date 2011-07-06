from userena.forms import AuthenticationForm

from .forms import I4PSignupForm

def member_forms(request):
    """
    Signin and signup forms (for the upper panel)
    """
    additions = {
        'signin_form': I4PSignupForm(),
        'signup_form': AuthenticationForm(),
    }
    return additions













