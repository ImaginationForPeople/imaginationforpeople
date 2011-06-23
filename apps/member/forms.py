from django import forms
from userena.forms import SignupForm
from apps.i4p_base.utils import remove_accents
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class I4PSignupForm(SignupForm):
    first_name = forms.CharField(_(u'first name'))
    last_name = forms.CharField(_(u'last name'))

    def __init__(self, *args, **kwargs):
        super(I4PSignupForm, self).__init__(*args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder = ['first_name',
                                 'last_name',
                                 'email',
                                 'password1',
                                 'password2']


    def save(self):
        firstname = self.cleaned_data['first_name'].title()
        lastname = self.cleaned_data['last_name'].title()
        username = remove_accents("%s%s".replace(" ", "").replace("-", "") % (firstname, lastname))
        users = User.objects.filter(username__istartswith=username)
        if users.count() > 0:
            username = "%s%s" % (username, users.count())

        self.cleaned_data['username'] = username

        return super(I4PSignupForm, self).save()
