# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import base64
from logging import getLogger

import requests

from ._compatimports import urlparse


log = getLogger(__name__)


class _BugzillaSession(object):
    """
    Class to handle the backend agnostic 'requests' setup
    """
    def __init__(self, url, user_agent,
            cookiecache=None, sslverify=True, cert=None,
            tokencache=None, api_key=None):
        self._url = url
        self._user_agent = user_agent
        self._scheme = urlparse(url)[0]
        self._cookiecache = cookiecache
        self._tokencache = tokencache
        self._api_key = api_key

        if self._scheme not in ["http", "https"]:
            raise Exception("Invalid URL scheme: %s (%s)" % (
                self._scheme, url))

        self._session = requests.Session()
        if cert:
            self._session.cert = cert
        if self._cookiecache:
            self._session.cookies = self._cookiecache.get_cookiejar()

        self._session.verify = sslverify
        self._session.headers["User-Agent"] = self._user_agent
        self._session.params["Bugzilla_api_key"] = self._api_key
        self._set_tokencache_param()

    def get_user_agent(self):
        return self._user_agent
    def get_scheme(self):
        return self._scheme
    def get_api_key(self):
        return self._api_key
    def get_token_value(self):
        return self._tokencache.get_value(self._url)
    def set_token_value(self, value):
        self._tokencache.set_value(self._url, value)
        self._set_tokencache_param()
    def set_content_type(self, value):
        self._session.headers["Content-Type"] = value

    def _set_tokencache_param(self):
        token = self.get_token_value()
        self._session.params["Bugzilla_token"] = token

    def set_basic_auth(self, user, password):
        """
        Set basic authentication method.
        """
        formatstr = "{}:{}".format(user, password).encode("utf-8")
        b64str = base64.b64encode(formatstr).decode("utf-8")
        authstr = "Basic {}".format(b64str)
        self._session.headers["Authorization"] = authstr

    def set_response_cookies(self, response):
        """
        Save any cookies received from the passed requests response
        """
        self._cookiecache.set_cookies(response.cookies)

    def get_requests_session(self):
        return self._session
