from django.db import models

# Create your models here.
from userena.models import UserenaLanguageBaseProfile
from django_countries import CountryField

class I4pProfile(UserenaLanguageBaseProfile):
    about = models.TextField()
    website = models.URLField()
    address = models.TextField()
    country = CountryField()
    
    