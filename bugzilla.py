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
import os.path, base64

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
        self._products   = None 
        self._components = dict()
        if 'cookies' in kwargs:
            self._readcookiefile(kwargs['cookies'])
        if 'url' in kwargs:
            self.connect(kwargs['url'])
        if 'user' in kwargs:
            self.user = kwargs['user']
        if 'password' in kwargs:
            self.password = kwargs['password']

    #---- Methods for establishing bugzilla connection and logging in

    def _readcookiefile(self,cookiefile):
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

    # Note that the bugzilla methods will ignore an empty user/password if you
    # send authentication info as a cookie in the request headers. So it's
    # OK if we keep sending empty / bogus login info in other methods.
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

    #---- Methods and properties with basic bugzilla info 

    def _get_queryinfo(self,force_refresh=False):
        '''Calls getQueryInfo, which returns a (quite large!) structure that
        contains all of the query data and query defaults for the bugzilla
        instance. Since this is a weighty call - takes a good 5-10sec on
        bugzilla.redhat.com - we load the info in this private method and the
        user instead plays with the querydata and querydefaults attributes of
        the bugzilla object.'''
        # Only fetch the data if we don't already have it, or are forced to
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

    def getproducts(self,force_refresh=False):
        '''Return a dict of product names and product descriptions.'''
        if force_refresh or not self._products:
            p = self._proxy.bugzilla.getProdInfo(self.user, self.password)
            self._products = p
        return self._products
    # Bugzilla.products is a property - we cache the product list on the first
    # call and return it for each subsequent call.
    products = property(fget=lambda self: self.getproducts(),
                        fdel=lambda self: setattr(self,'_products',None))

    def getcomponents(self,product,force_refresh=False):
        '''Return a dict of components for the given product.'''
        if force_refresh or product not in self._components:
            c = self._proxy.bugzilla.getProdCompInfo(product, 
                                                     self.user,self.password)
            self._components[product] = c
        return self._components[product]
    # TODO - add a .components property that acts like a dict?

    #---- Methods for reading bugs

    def getbug(self,id):
        '''Return a dict of full bug info for the given bug id'''
        return self._proxy.bugzilla.getBug(id, self.user, self.password)

    def getbugsimple(self,id):
        '''Return a short dict of simple bug info for the given bug id'''
        return self._proxy.bugzilla.getBugSimple(id, self.user, self.password)

    def query(self,query):
        '''Query bugzilla and return a list of matching bugs.
        query must be a dict with fields like those in in querydata['fields'].

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

    def getwhiteboard(self,id,which):
        '''Get the current value of the whiteboard specified by 'which' on bug
        with the the given id.'''
        raise NotImplementedError

    #---- Methods for modifying existing bugs

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
    
    def setstatus(self,id,status):
        raise NotImplementedError

    def closebug(self,id):
        raise NotImplementedError
    
    def setwhiteboard(self,id,type,data):
        raise NotImplmementedError

    def setassignee(self,id,assignee):
        raise NotImplementedError

    def updatedeps(self,id,deplist):
        raise NotImplementedError

    def updatecc(self,id,cclist):
        raise NotImplementedError

    #---- Methods for working with attachments

    def __attachment_encode(self,fh):
        '''Return the contents of the file-like object fh in a form
        appropriate for attaching to a bug in bugzilla.'''
        # Read data in chunks so we don't end up with two copies of the file
        # in RAM.
        chunksize = 3072 # base64 encoding wants input in multiples of 3
        data = ''
        chunk = fh.read(chunksize)
        while chunk:
            # we could use chunk.encode('base64') but that throws a newline
            # at the end of every output chunk, which increases the size of
            # the output.
            data = data + base64.b64encode(chunk)
            chunk = fh.read(chunksize)
        return data

    def attachfile(self,id,attachfile,description,**kwargs):
        '''Attach a file to the given bug ID. Returns the ID of the attachment
        or raises xmlrpclib.Fault if something goes wrong.
        attachfile may be a filename (which will be opened) or a file-like
        object, which must provide a 'read' method. If it's not one of these,
        this method will raise a TypeError.
        description is the short description of this attachment.
        Optional keyword args are as follows:
            filename:  this will be used as the filename for the attachment.
                       REQUIRED if attachfile is a file-like object with no
                       'name' attribute, otherwise the filename or .name
                       attribute will be used.
            comment:   An optional comment about this attachment.
            isprivate: Set to True if the attachment should be marked private.
            ispatch:   Set to True if the attachment is a patch.
            contenttype: The mime-type of the attached file. Defaults to
                         application/octet-stream if not set. NOTE that text
                         files will *not* be viewable in bugzilla unless you 
                         remember to set this to text/plain. So remember that!
        '''
        if isinstance(attachfile,str):
            f = open(attachfile)
        elif hasattr(attachfile,'read'):
            f = attachfile
        else:
            raise TypeError, "attachfile must be filename or file-like object"
        kwargs['description'] = description
        if 'filename' not in kwargs:
            kwargs['filename'] = os.path.basename(f.name)
        # TODO: guess contenttype?
        if 'contenttype' not in kwargs:
            kwargs['contenttype'] = 'application/octet-stream'
        kwargs['data'] = self.__attachment_encode(f)
        (attachid, mailresults) = server._proxy.bugzilla.addAttachment(id,kwargs,self.user,self.password)
        return attachid

    def openattachment(self,attachid):
        '''Get the contents of the attachment with the given attachment ID.
        Returns a file-like object.'''
        att_uri = self._url.replace('xmlrpc.cgi','attachment.cgi')
        att_uri = att_uri + '?%i' % attachid
        att = urllib2.urlopen(att_uri)
        # RFC 2183 defines the content-disposition header, if you're curious
        disp = att.headers['content-disposition'].split(';')
        [filename_parm] = [i for i in disp if i.strip().startswith('filename=')]
        (dummy,filename) = filename_parm.split('=')
        # RFC 2045/822 defines the grammar for the filename value, but
        # I think we just need to remove the quoting. I hope.
        att.name = filename.strip('"')
        # Hooray, now we have a file-like object with .read() and .name
        return att

    def createbug(self,**kwargs):
        '''Create a bug with the given info. Returns the bug ID.'''
        raise NotImplementedError

    # TODO: allow simple 'tagging' by adding/removing text to whiteboard(s)
    # TODO: flag handling?

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
