# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import base64
from logging import getLogger
import sys

# pylint: disable=import-error
if sys.version_info[0] >= 3:
    from configparser import ConfigParser
    from urllib.parse import urlparse  # pylint: disable=no-name-in-module
    from xmlrpc.client import Fault, ProtocolError, ServerProxy, Transport
else:
    from ConfigParser import SafeConfigParser as ConfigParser
    from urlparse import urlparse
    from xmlrpclib import Fault, ProtocolError, ServerProxy, Transport
# pylint: enable=import-error

import requests

from .exceptions import BugzillaError


log = getLogger(__name__)


class _BugzillaTokenCache(object):
    """
    Cache for tokens, including, with apologies for the duplicative
    terminology, both Bugzilla Tokens and API Keys.
    """

    def __init__(self, uri, tokenfilename):
        self.tokenfilename = tokenfilename
        self.tokenfile = ConfigParser()
        self.domain = urlparse(uri)[1]

        if self.tokenfilename:
            self.tokenfile.read(self.tokenfilename)

        if self.domain not in self.tokenfile.sections():
            self.tokenfile.add_section(self.domain)

    @property
    def value(self):
        if self.tokenfile.has_option(self.domain, 'token'):
            return self.tokenfile.get(self.domain, 'token')
        else:
            return None

    @value.setter
    def value(self, value):
        if self.value == value:
            return

        if value is None:
            self.tokenfile.remove_option(self.domain, 'token')
        else:
            self.tokenfile.set(self.domain, 'token', value)

        if self.tokenfilename:
            with open(self.tokenfilename, 'w') as tokenfile:
                log.debug("Saving to tokenfile")
                self.tokenfile.write(tokenfile)

    def __repr__(self):
        return '<Bugzilla Token Cache :: %s>' % self.value


class _BugzillaSession(object):
    """
    Class to handle the backend agnostic 'requests' setup
    """
    def __init__(self, url, user_agent,
            cookiejar=None, sslverify=True, sslcafile=None, cert=None,
            tokenfile=None, api_key=None):
        self._user_agent = user_agent
        self._scheme = urlparse(url)[0]
        self._cookiejar = cookiejar
        self._token_cache = _BugzillaTokenCache(url, tokenfile)
        self._api_key = api_key

        if self._scheme not in ["http", "https"]:
            raise Exception("Invalid URL scheme: %s (%s)" % (
                self._scheme, url))
        use_https = self._scheme == 'https'

        self._request_defaults = {
            'cert': sslcafile if use_https else None,
            'cookies': self._cookiejar,
            'verify': sslverify,
            'headers': {
                'Content-Type': 'text/xml',
                'User-Agent': self._user_agent,
            }
        }

        # Using an explicit Session, rather than requests.get, will use
        # HTTP KeepAlive if the server supports it.
        self._session = requests.Session()
        if cert:
            self._session.cert = cert

    def get_user_agent(self):
        return self._user_agent
    def get_scheme(self):
        return self._scheme
    def get_api_key(self):
        return self._api_key
    def get_token_cache(self):
        return self._token_cache

    def set_basic_auth(self, user, password):
        """
        Set basic authentication method.
        """
        b64str = str(base64.b64encode("{}:{}".format(user, password)))
        authstr = "Basic {}".format(b64str.encode("utf-8").decode("utf-8"))
        self._request_defaults["headers"]["Authorization"] = authstr

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

    def post(self, url, data):
        return self._session.post(url, data=data, **self._request_defaults)


class _BugzillaXMLRPCTransport(Transport):
    def __init__(self, bugzillasession):
        if hasattr(Transport, "__init__"):
            Transport.__init__(self, use_datetime=False)

        self.__bugzillasession = bugzillasession
        self.__seen_valid_xml = False

        # Override Transport.user_agent
        self.user_agent = self.__bugzillasession.get_user_agent()


    ############################
    # Bugzilla private helpers #
    ############################

    def __request_helper(self, url, request_body):
        """
        A helper method to assist in making a request and parsing the response.
        """
        response = None
        # pylint: disable=try-except-raise
        try:
            response = self.__bugzillasession.post(url, request_body)

            # We expect utf-8 from the server
            response.encoding = 'UTF-8'

            # update/set any cookies
            self.__bugzillasession.set_response_cookies(response)

            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException as e:
            if not response:
                raise
            raise ProtocolError(
                url, response.status_code, str(e), response.headers)
        except Fault:
            raise
        except Exception:
            msg = str(sys.exc_info()[1])
            if not self.__seen_valid_xml:
                msg += "\nThe URL may not be an XMLRPC URL: %s" % url
            e = BugzillaError(msg)
            # pylint: disable=attribute-defined-outside-init
            e.__traceback__ = sys.exc_info()[2]
            # pylint: enable=attribute-defined-outside-init
            raise e


    ######################
    # Tranport overrides #
    ######################

    def parse_response(self, response):
        """
        Override Transport.parse_response
        """
        parser, unmarshaller = self.getparser()
        msg = response.text.encode('utf-8')
        try:
            parser.feed(msg)
        except Exception:
            log.debug("Failed to parse this XMLRPC response:\n%s", msg)
            raise

        self.__seen_valid_xml = True
        parser.close()
        return unmarshaller.close()

    def request(self, host, handler, request_body, verbose=0):
        """
        Override Transport.request
        """
        # Setting self.verbose here matches overrided request() behavior
        # pylint: disable=attribute-defined-outside-init
        self.verbose = verbose

        url = "%s://%s%s" % (self.__bugzillasession.get_scheme(),
                host, handler)

        # xmlrpclib fails to escape \r
        request_body = request_body.replace(b'\r', b'&#xd;')

        return self.__request_helper(url, request_body)


class _BugzillaXMLRPCProxy(ServerProxy, object):
    """
    Override of xmlrpc ServerProxy, to insert bugzilla API auth
    into the XMLRPC request data
    """
    def __init__(self, uri, bugzillasession, *args, **kwargs):
        self.__bugzillasession = bugzillasession
        transport = _BugzillaXMLRPCTransport(self.__bugzillasession)
        ServerProxy.__init__(self, uri, transport, *args, **kwargs)

    def _ServerProxy__request(self, methodname, params):
        """
        Overrides ServerProxy _request method
        """
        if len(params) == 0:
            params = ({}, )

        log.debug("XMLRPC call: %s(%s)", methodname, params[0])
        api_key = self.__bugzillasession.get_api_key()
        token_cache = self.__bugzillasession.get_token_cache()

        if api_key is not None:
            if 'Bugzilla_api_key' not in params[0]:
                params[0]['Bugzilla_api_key'] = api_key
        elif token_cache.value is not None:
            if 'Bugzilla_token' not in params[0]:
                params[0]['Bugzilla_token'] = token_cache.value

        # pylint: disable=no-member
        ret = ServerProxy._ServerProxy__request(self, methodname, params)
        # pylint: enable=no-member

        if isinstance(ret, dict) and 'token' in ret.keys():
            token_cache.value = ret.get('token')
        return ret
