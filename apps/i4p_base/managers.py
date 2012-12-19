from django.contrib.sites.managers import CurrentSiteManager

from hvad.manager import TranslationManager

class CurrentSiteTranslationManager(CurrentSiteManager, TranslationManager):
    """
    A translation and multisite aware manager. Happily, both
    doesn't override the same methods
    """
    pass
