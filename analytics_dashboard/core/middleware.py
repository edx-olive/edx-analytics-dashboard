"""
Middleware for Language Preferences
"""

import logging
from lang_pref_middleware import middleware

from django.template.response import TemplateResponse

from core.exceptions import ServiceUnavailableError
from waffle import flag_is_active

logger = logging.getLogger(__name__)


# For https://tasks.opencraft.com/browse/SE-3950 . If an upstream solution is invented by the time you're rebasing this,
# remove it and the line that includes it from the middleware settings.
class LanguageHeaderPreemptMiddleware(object):
    """
    If the appropriate waffle flag is present, ignore the 'Accept-Language' header.
    """
    def process_request(self, request):
        if not flag_is_active(request, 'analytics_dashboard.ignore_accept_language'):
            return
        if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
            del request.META['HTTP_ACCEPT_LANGUAGE']


class LanguagePreferenceMiddleware(middleware.LanguagePreferenceMiddleware):
    def get_user_language_preference(self, user):
        """
        Retrieve the given user's language preference.

        Returns None if no preference set.
        """
        return user.language


class ServiceUnavailableExceptionMiddleware(object):
    """
    Display an error template for 502 errors.
    """

    def process_exception(self, request, exception):
        if isinstance(exception, ServiceUnavailableError):
            logger.exception(exception)
            return TemplateResponse(request, '503.html', status=503)
