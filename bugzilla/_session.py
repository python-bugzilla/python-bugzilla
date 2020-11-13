# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

from logging import getLogger

import os
import sys
import urllib.parse

import requests


log = getLogger(__name__)


class _BugzillaSession(object):
    """
    Class to handle the backend agnostic 'requests' setup
    """
    def __init__(self, url, user_agent,
            cookiecache, sslverify, cert,
            tokencache, api_key, requests_session=None):
        self._url = url
        self._user_agent = user_agent
        self._scheme = urllib.parse.urlparse(url)[0]
        self._cookiecache = cookiecache
        self._tokencache = tokencache
        self._api_key = api_key
        self._is_xmlrpc = False

        if self._scheme not in ["http", "https"]:
            raise Exception("Invalid URL scheme: %s (%s)" % (
                self._scheme, url))

        self._session = requests_session
        if not self._session:
            self._session = requests.Session()

        if cert:
            self._session.cert = cert
        if self._cookiecache:
            self._session.cookies = self._cookiecache.get_cookiejar()
        if sslverify is False:
            self._session.verify = False
        self._session.headers["User-Agent"] = self._user_agent
        self._set_tokencache_param()

    def _get_timeout(self):
        # Default to 5 minutes. This is longer than bugzilla.redhat.com's
        # apparent 3 minute timeout so shouldn't affect legitimate usage,
        # but saves us from indefinite hangs
        DEFAULT_TIMEOUT = 300
        envtimeout = os.environ.get("PYTHONBUGZILLA_REQUESTS_TIMEOUT")
        return float(envtimeout or DEFAULT_TIMEOUT)

    def set_rest_defaults(self):
        self._session.headers["Content-Type"] = "application/json"
        # Bugzilla 5.0 only supports api_key as a query parameter.
        # Bugzilla 5.1+ takes it as a X-BUGZILLA-API-KEY header as well,
        # with query param taking preference.
        self._session.params["Bugzilla_api_key"] = self._api_key
    def set_xmlrpc_defaults(self):
        self._is_xmlrpc = True
        self._session.headers["Content-Type"] = "text/xml"

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

    def _set_tokencache_param(self):
        if self._api_key:
            # Don't add a token to the params list if an API key is set.
            # Keeping API key solo means bugzilla will definitely fail
            # if the key expires. Passing in a token could hide that
            # fact, which could make it confusing to pinpoint the issue.
            return
        token = self.get_token_value()
        self._session.params["Bugzilla_token"] = token

    def set_response_cookies(self, response):
        """
        Save any cookies received from the passed requests response
        """
        self._cookiecache.set_cookies(response.cookies)

    def get_requests_session(self):
        return self._session

    def request(self, *args, **kwargs):
        timeout = self._get_timeout()
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout

        response = self._session.request(*args, **kwargs)

        if self._is_xmlrpc:
            # Yes this still appears to matter for properly decoding unicode
            # code points in bugzilla.redhat.com content
            response.encoding = "UTF-8"
            # Set response cookies
            self.set_response_cookies(response)

        try:
            response.raise_for_status()
        except Exception as e:
            # Scrape the api key out of the returned exception string
            message = str(e).replace(self._api_key or "", "")
            raise type(e)(message).with_traceback(sys.exc_info()[2])

        return response
