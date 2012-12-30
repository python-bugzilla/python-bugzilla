# base.py - the base classes etc. for a Python interface to bugzilla
#
# Copyright (C) 2007, 2008, 2009, 2010 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import cookielib
import xmlrpclib
import urllib2

from bugzilla import log


class CookieResponse:
    '''Fake HTTPResponse object that we can fill with headers we got elsewhere.
    We can then pass it to CookieJar.extract_cookies() to make it pull out the
    cookies from the set of headers we have.'''
    def __init__(self, headers):
        self.headers = headers

    def info(self):
        return self.headers


class CookieTransport(xmlrpclib.Transport):
    '''A subclass of xmlrpclib.Transport that supports cookies.'''
    cookiejar = None
    scheme = 'http'

    def __init__(self, *args, **kwargs):
        self.verbose = False
        xmlrpclib.Transport.__init__(self, *args, **kwargs)

    # Cribbed from xmlrpclib.Transport.send_user_agent
    def send_cookies(self, connection, cookie_request):
        if self.cookiejar is None:
            self.cookiejar = cookielib.CookieJar()
        elif self.cookiejar:
            # Let the cookiejar figure out what cookies are appropriate
            self.cookiejar.add_cookie_header(cookie_request)
            # Pull the cookie headers out of the request object...
            cookielist = []
            for h, v in cookie_request.header_items():
                if h.startswith('Cookie'):
                    cookielist.append([h, v])
            # ...and put them over the connection
            for h, v in cookielist:
                connection.putheader(h, v)

    # This is the same request() method from python 2.6's xmlrpclib.Transport,
    # with a couple additions noted below
    def request_with_cookies(self, host, handler, request_body, verbose=0):
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        # ADDED: construct the URL and Request object for
        # proper cookie handling
        request_url = "%s://%s%s" % (self.scheme, host, handler)
        cookie_request = urllib2.Request(request_url)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        # ADDED. creates cookiejar if None.
        self.send_cookies(h, cookie_request)
        self.send_user_agent(h)
        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()

        # ADDED: parse headers and get cookies here
        cookie_response = CookieResponse(headers)
        # Okay, extract the cookies from the headers
        self.cookiejar.extract_cookies(cookie_response, cookie_request)
        # And write back any changes
        if hasattr(self.cookiejar, 'save'):
            try:
                self.cookiejar.save(self.cookiejar.filename)
            except Exception, e:
                log.error("Couldn't write cookiefile %s: %s" %
                          (self.cookiejar.filename, str(e)))

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers)

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        # pylint: disable=E1101
        ret = self._parse_response(h.getfile(), sock)
        # pylint: enable=E1101
        return ret

    # This is just python 2.7's xmlrpclib.Transport.single_request, with
    # send additions noted below to send cookies along with the request
    def single_request_with_cookies(self, host, handler,
                                    request_body, verbose=0):
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        # ADDED: construct the URL and Request object for
        # proper cookie handling
        request_url = "%s://%s%s" % (self.scheme, host, handler)
        cookie_request = urllib2.Request(request_url)

        try:
            self.send_request(h, handler, request_body)
            self.send_host(h, host)
            # ADDED. creates cookiejar if None.
            self.send_cookies(h, cookie_request)
            self.send_user_agent(h)
            self.send_content(h, request_body)

            response = h.getresponse(buffering=True)

            # ADDED: parse headers and get cookies here
            cookie_response = CookieResponse(response.msg)
            # Okay, extract the cookies from the headers
            self.cookiejar.extract_cookies(cookie_response, cookie_request)
            # And write back any changes
            if hasattr(self.cookiejar, 'save'):
                try:
                    self.cookiejar.save(self.cookiejar.filename)
                except Exception, e:
                    log.error("Couldn't write cookiefile %s: %s" %
                              (self.cookiejar.filename, str(e)))

            if response.status == 200:
                self.verbose = verbose
                return self.parse_response(response)
        except xmlrpclib.Fault:
            raise
        except Exception:
            # All unexpected errors leave connection in
            # a strange state, so we clear it.
            self.close()
            raise

        # discard any response data and raise exception
        if (response.getheader("content-length", 0)):
            response.read()
        raise xmlrpclib.ProtocolError(
            host + handler,
            response.status, response.reason,
            response.msg)

    # Override the appropriate request method
    if hasattr(xmlrpclib.Transport, 'single_request'):
        # python 2.7+
        single_request = single_request_with_cookies
    else:
        # python 2.6 and earlier
        request = request_with_cookies


class SafeCookieTransport(xmlrpclib.SafeTransport, CookieTransport):
    '''SafeTransport subclass that supports cookies.'''
    scheme = 'https'
    # Override the appropriate request method
    if hasattr(xmlrpclib.Transport, 'single_request'):
        single_request = CookieTransport.single_request_with_cookies
    else:
        request = CookieTransport.request_with_cookies
