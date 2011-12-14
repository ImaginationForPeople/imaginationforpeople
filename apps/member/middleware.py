from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils import translation
from django.utils.translation.trans_real import parse_accept_lang_header

from localeurl.middleware import LocaleURLMiddleware as BaseLocaleURLMiddleware
from localeurl import settings as localeurl_settings
from localeurl import utils

class LocaleURLMiddleware(BaseLocaleURLMiddleware):

    def process_request(self, request):
        """
        Override django-localeurl request middleware so that is looks into the
        profile language to determine the current locale before checking browser
        settings.
        """
        locale, path = utils.strip_path(request.path_info)
        if not locale:
            # If URL doesn't contain any locale info
            if request.user.is_authenticated():
                # Get locale from the user profile
                profile = request.user.get_profile()
                locale = profile.language
            elif localeurl_settings.USE_ACCEPT_LANGUAGE:
                # Get locale from browser settings
                accept_langs = filter(lambda x: x, [utils.supported_language(lang[0])
                                                    for lang in
                                                    parse_accept_lang_header(
                            request.META.get('HTTP_ACCEPT_LANGUAGE', ''))])
                if accept_langs:
                    locale = accept_langs[0]
        locale_path = utils.locale_path(path, locale)
        if locale_path != request.path_info:
            if request.META.get("QUERY_STRING", ""):
                locale_path = "%s?%s" % (locale_path,
                        request.META['QUERY_STRING'])
            return HttpResponsePermanentRedirect(locale_path)
        request.path_info = path
        if not locale:
            try:
                locale = request.LANGUAGE_CODE
            except AttributeError:
                locale = settings.LANGUAGE_CODE
        translation.activate(locale)
        request.LANGUAGE_CODE = translation.get_language()
