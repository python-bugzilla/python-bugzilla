#!/usr/bin/python
# bugzilla.py - a Python interface to Bugzilla, using xmlrpclib.
#
# Copyright (C) 2007 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import xmlrpclib, urllib2, cookielib

version = '0.1'
user_agent = 'bugzilla.py/%s (Python-urllib2/%s)' % \
        (version,urllib2.__version__)

class Bugzilla(object):
    def __init__(self,**kwargs):
        # Settings the user might want to tweak
        self.user       = ''
        self.password   = ''
        self.url        = ''
        # Bugzilla object state info that users shouldn't mess with
        self._cookiejar  = None
        self._proxy      = None
        self._opener     = None
        self._querydata  = None
        self._querydefaults = None
        if 'cookies' in kwargs:
            self.readcookiefile(kwargs['cookies'])
        if 'url' in kwargs:
            self.connect(kwargs['url'])
        if 'user' in kwargs:
            self.user = kwargs['user']
        if 'password' in kwargs:
            self.password = kwargs['password']

    def readcookiefile(self,cookiefile):
        '''Read the given (Mozilla-style) cookie file and fill in the cookiejar,
        allowing us to use the user's saved credentials to access bugzilla.'''
        cj = cookielib.MozillaCookieJar()
        cj.load(cookiefile)
        self._cookiejar = cj
        self._cookiejar.filename = cookiefile

    def connect(self,url):
        '''Connect to the bugzilla instance with the given url.'''
        # Set up the transport
        if url.startswith('https'):
            self._transport = SafeCookieTransport()
        else:
            self._transport = CookieTransport() 
        self._transport.user_agent = user_agent
        self._transport.cookiejar = self._cookiejar or cookielib.CookieJar()
        # Set up the proxy, using the transport
        self._proxy = xmlrpclib.ServerProxy(url,self._transport)
        # Set up the urllib2 opener (using the same cookiejar)
        handler = urllib2.HTTPCookieProcessor(self._cookiejar)
        self._opener = urllib2.build_opener(handler)
        self._opener.addheaders = [('User-agent',user_agent)]

    def login(self,user,password):
        '''Attempt to log in using the given username and password. Subsequent
        method calls will use this username and password. Returns False if 
        login fails, otherwise returns a dict of user info.
        
        Note that it is not required to login before calling other methods;
        you may just set user and password and call whatever methods you like.
        '''
        self.user = user
        self.password = password
        try: 
            r = self._proxy.bugzilla.login(self.user,self.password)
        except xmlrpclib.Fault, f:
            r = False
        return r

    # Note that the bugzilla methods will ignore an empty user/password if you
    # send authentication info as a cookie in the request headers. So it's
    # OK if we keep sending empty / bogus login info.

    # ARGLE this should use properties or do some kind of caching or something
    def components(self,product):
        '''Return a dict of components for the given product.'''
        return self._proxy.bugzilla.getProdCompInfo(product, self.user, 
                                                             self.password)

    def products(self):
        '''Return a dict of product names and product descriptions.'''
        return self._proxy.bugzilla.getProdInfo(self.user, self.password)

    def getbug(self,id):
        '''Return a dict of full bug info for the given bug id'''
        return self._proxy.bugzilla.getBug(id, self.user, self.password)

    def getbugsimple(self,id):
        '''Return a short dict of simple bug info for the given bug id'''
        return self._proxy.bugzilla.getBugSimple(id, self.user, self.password)

    def addcomment(self,id,comment,private=False,
                   timestamp='',worktime='',bz_gid=''):
        '''Add a comment to the bug with the given ID. Other optional 
        arguments are as follows:
            private:   if True, mark this comment as private.
            timestamp: comment timestamp, in the form "YYYY-MM-DD HH:MM:SS"
            worktime:  amount of time spent on this comment (undoc in upstream)
            bz_gid:    if present, and the entire bug is *not* already private
                       to this group ID, this comment will be marked private.'''
        return self._proxy.bugzilla.addComment(id,comment,
                   self.user,self.password,private,timestamp,worktime,bz_gid)

    # Bug querying functions. These are not very well commented. Sorry.

    def __get_queryinfo(self,force_refresh=False):
        '''Calls getQueryInfo, which returns a (quite large!) structure that
        contains all of the query data and query defaults for the bugzilla
        instance. Since this is a weighty call - takes a good 5-10sec on
        bugzilla.redhat.com - we load the info in this private method and the
        user instead plays with the querydata and querydefaults attributes of
        the bugzilla object.'''
        # Only fetch the data if we don't already have it, or forced to
        if force_refresh or not (self._querydata and self._querydefaults):
            qi = self._proxy.bugzilla.getQueryInfo(self.user,self.password)
            (self._querydata, self._querydefaults) = qi
        return (self._querydata, self._querydefaults)

    # Set querydata and querydefaults as properties so they auto-create
    # themselves when touched by a user. This bit was lifted from YumBase,
    # because skvidal is much smarter than I am.
    querydata = property(fget=lambda self: self.__get_queryinfo()[0],
                         fdel=lambda self: setattr(self,"_querydata",None))
    querydefaults = property(fget=lambda self: self.__get_queryinfo()[1],
                         fdel=lambda self: setattr(self,"_querydefaults",None))

    def query(self,query):
        '''Query bugzilla and return a list of matching bugs.
        query should be a dict that matches the fields in querydata['fields']..
        or something.

        Returns a dict like this: {'bugs':buglist,
                                   'displaycolumns':columnlist,
                                   'sql':querystring}
        
        buglist is a list of dicts describing bugs. You can specify which 
        columns/keys will be listed in the bugs by setting 'column_list' in
        the query; otherwise the default columns are used (see the list in
        querydefaults['default_column_list']). The list of columns will be
        in 'displaycolumns', and the SQL query used by this query will be in
        'sql'. 
        ''' 
        return self._proxy.bugzilla.runQuery(query,self.user,self.password)

    # TODO: createbug, attachfile, searchbugs, setstatus, closebug, 
    #       setassignee, updatedeps, setwhiteboard, updatecc
    # TODO: allow 'tagging' by adding text to the whiteboard(s)
    # TODO: flags?

class CookieTransport(xmlrpclib.Transport):
    '''A subclass of xmlrpclib.Transport that supports cookies.'''
    cookiejar = None
    scheme = 'http'

    # Cribbed from xmlrpclib.Transport.send_user_agent 
    def send_cookies(self, connection, cookie_request):
        if self.cookiejar is None:
            self.cookiejar = cookielib.CookieJar()
        elif self.cookiejar:
            # Let the cookiejar figure out what cookies are appropriate
            self.cookiejar.add_cookie_header(cookie_request)
            # Pull the cookie headers out of the request object...
            cookielist=list()
            for h,v in cookie_request.header_items():
                if h.startswith('Cookie'):
                    cookielist.append([h,v])
            # ...and put them over the connection
            for h,v in cookielist:
                connection.putheader(h,v)

    # This is the same request() method from xmlrpclib.Transport,
    # with a couple additions noted below
    def request(self, host, handler, request_body, verbose=0):
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        # ADDED: construct the URL and Request object for proper cookie handling
        request_url = "%s://%s/" % (self.scheme,host)
        cookie_request  = urllib2.Request(request_url) 

        self.send_request(h,handler,request_body)
        self.send_host(h,host) 
        self.send_cookies(h,cookie_request) # ADDED. creates cookiejar if None.
        self.send_user_agent(h)
        self.send_content(h,request_body)

        errcode, errmsg, headers = h.getreply()

        # ADDED: parse headers and get cookies here
        # fake a response object that we can fill with the headers above
        class CookieResponse:
            def __init__(self,headers): self.headers = headers
            def info(self): return self.headers
        cookie_response = CookieResponse(headers)
        # Okay, extract the cookies from the headers
        self.cookiejar.extract_cookies(cookie_response,cookie_request)
        # And write back any changes
        if hasattr(self.cookiejar,'save'):
            self.cookiejar.save(self.cookiejar.filename)

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        return self._parse_response(h.getfile(), sock)

class SafeCookieTransport(xmlrpclib.SafeTransport,CookieTransport):
    '''SafeTransport subclass that supports cookies.'''
    scheme = 'https'
    request = CookieTransport.request
