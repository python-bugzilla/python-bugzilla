# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from logging import getLogger
import sys

if hasattr(sys.version_info, "major") and sys.version_info.major >= 3:
    # pylint: disable=import-error,no-name-in-module
    from configparser import SafeConfigParser
    from urllib.parse import urlparse
    from xmlrpc.client import Fault, ProtocolError, ServerProxy, Transport
else:
    from ConfigParser import SafeConfigParser
    from urlparse import urlparse  # pylint: disable=ungrouped-imports
    from xmlrpclib import Fault, ProtocolError, ServerProxy, Transport

import requests


log = getLogger(__name__)


class BugzillaError(Exception):
    '''Error raised in the Bugzilla client code.'''
    pass


class _BugzillaToken(object):
    def __init__(self, uri, tokenfilename):
        self.tokenfilename = tokenfilename
        self.tokenfile = SafeConfigParser()
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
        return '<Bugzilla Token :: %s>' % (self.value)


class _BugzillaServerProxy(ServerProxy):
    def __init__(self, uri, tokenfile, *args, **kwargs):
        # pylint: disable=super-init-not-called
        # No idea why pylint complains here, must be a bug
        ServerProxy.__init__(self, uri, *args, **kwargs)
        self.token = _BugzillaToken(uri, tokenfile)

    def clear_token(self):
        self.token.value = None

    def _ServerProxy__request(self, methodname, params):
        if self.token.value is not None:
            if len(params) == 0:
                params = ({}, )

            if 'Bugzilla_token' not in params[0]:
                params[0]['Bugzilla_token'] = self.token.value

        # pylint: disable=maybe-no-member
        ret = ServerProxy._ServerProxy__request(self, methodname, params)
        # pylint: enable=maybe-no-member

        if isinstance(ret, dict) and 'token' in ret.keys():
            self.token.value = ret.get('token')
        return ret


class _RequestsTransport(Transport):
    user_agent = 'Python/Bugzilla'

    def __init__(self, url, cookiejar=None,
                 sslverify=True, sslcafile=None, debug=0):
        # pylint: disable=W0231
        # pylint does not handle multiple import of Transport well
        if hasattr(Transport, "__init__"):
            Transport.__init__(self, use_datetime=False)

        self.verbose = debug
        self._cookiejar = cookiejar

        # transport constructor needs full url too, as xmlrpc does not pass
        # scheme to request
        self.scheme = urlparse(url)[0]
        if self.scheme not in ["http", "https"]:
            raise Exception("Invalid URL scheme: %s (%s)" % (self.scheme, url))

        self.use_https = self.scheme == 'https'

        self.request_defaults = {
            'cert': sslcafile if self.use_https else None,
            'cookies': cookiejar,
            'verify': sslverify,
            'headers': {
                'Content-Type': 'text/xml',
                'User-Agent': self.user_agent,
            }
        }

        # Using an explicit Session, rather than requests.get, will use
        # HTTP KeepAlive if the server supports it.
        self.session = requests.Session()

    def parse_response(self, response):
        """ Parse XMLRPC response """
        parser, unmarshaller = self.getparser()
        parser.feed(response.text.encode('utf-8'))
        parser.close()
        return unmarshaller.close()

    def _request_helper(self, url, request_body):
        """
        A helper method to assist in making a request and provide a parsed
        response.
        """
        response = None
        try:
            response = self.session.post(
                url, data=request_body, **self.request_defaults)

            # We expect utf-8 from the server
            response.encoding = 'UTF-8'

            # update/set any cookies
            if self._cookiejar is not None:
                for cookie in response.cookies:
                    self._cookiejar.set_cookie(cookie)

                if self._cookiejar.filename is not None:
                    # Save is required only if we have a filename
                    self._cookiejar.save()

            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException:
            e = sys.exc_info()[1]
            if not response:
                raise
            raise ProtocolError(
                url, response.status_code, str(e), response.headers)
        except Fault:
            raise sys.exc_info()[1]
        except Exception:
            # pylint: disable=W0201
            e = BugzillaError(str(sys.exc_info()[1]))
            e.__traceback__ = sys.exc_info()[2]
            raise e

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        url = "%s://%s%s" % (self.scheme, host, handler)

        # xmlrpclib fails to escape \r
        request_body = request_body.replace(b'\r', b'&#xd;')

        return self._request_helper(url, request_body)
