# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import base64
from logging import getLogger
import sys

# pylint: disable=import-error
if sys.version_info[0] >= 3:
    from urllib.parse import urlparse  # pylint: disable=no-name-in-module
else:
    from urlparse import urlparse
# pylint: enable=import-error

import requests

from ._authfiles import _BugzillaTokenCache


log = getLogger(__name__)


class _BugzillaSession(object):
    """
    Class to handle the backend agnostic 'requests' setup
    """
    def __init__(self, url, user_agent,
            cookiejar=None, sslverify=True, cert=None,
            tokenfile=None, api_key=None):
        self._user_agent = user_agent
        self._scheme = urlparse(url)[0]
        self._cookiejar = cookiejar
        self._token_cache = _BugzillaTokenCache(url, tokenfile)
        self._api_key = api_key

        if self._scheme not in ["http", "https"]:
            raise Exception("Invalid URL scheme: %s (%s)" % (
                self._scheme, url))

        self._session = requests.Session()
        if cert:
            self._session.cert = cert
        if self._cookiejar:
            self._session.cookies = self._cookiejar

        self._session.verify = sslverify
        self._session.headers["User-Agent"] = self._user_agent
        self._session.params["Bugzilla_api_key"] = self._api_key
        self._set_token_cache_param()

    def get_user_agent(self):
        return self._user_agent
    def get_scheme(self):
        return self._scheme
    def get_api_key(self):
        return self._api_key
    def get_token_value(self):
        return self._token_cache.get_value()
    def set_token_value(self, value):
        self._token_cache.set_value(value)
        self._set_token_cache_param()
    def set_content_type(self, value):
        self._session.headers["Content-Type"] = value

    def _set_token_cache_param(self):
        self._session.params["Bugzilla_token"] = self._token_cache.get_value()

    def set_basic_auth(self, user, password):
        """
        Set basic authentication method.
        """
        b64str = str(base64.b64encode("{}:{}".format(user, password)))
        authstr = "Basic {}".format(b64str.encode("utf-8").decode("utf-8"))
        self._session.headers["Authorization"] = authstr

    def set_response_cookies(self, response):
        """
        Save any cookies received from the passed requests response
        """
        if self._cookiejar is None:
            return

        for cookie in response.cookies:
            self._cookiejar.set_cookie(cookie)

        if self._cookiejar.filename is not None:
            # Save is required only if we have a filename
            self._cookiejar.save()

    def get_requests_session(self):
        return self._session
