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

import xmlrpclib, urllib2
try:
       import cookielib
except ImportError:
       import ClientCookie as cookielib
import os
import base64
import tempfile
import logging
import locale
import email.utils
from email.header import decode_header

log = logging.getLogger('bugzilla')

version = '0.6.2'
user_agent = 'Python-urllib2/%s bugzilla.py/%s' % \
        (urllib2.__version__,version)

class BugzillaError(Exception):
    '''Error raised in the Bugzilla client code.'''
    pass

class NeedSyncError(BugzillaError):
    '''Must save data from this class to the bugzilla server before using this.
    '''
    pass

class NeedParamError(BugzillaError):
    '''A necessary parameter was left out.'''
    pass

class LoadError(BugzillaError):
    '''Error loading credentials'''
    pass

def replace_getbug_errors_with_None(rawlist):
    '''r is a raw xmlrpc response.
    If it represents an error, None is returned.
    Otherwise, r is returned.
    This is mostly used for XMLRPC Multicall handling.'''
    # Yes, this is a naive implementation
    # XXX: return a generator?
    result = []
    for r in rawlist:
        if isinstance(r,dict) and 'bug_id' in r:
            result.append(r)
        else:
            result.append(None)
    return result

def decode_rfc2231_value(val):
    # BUG WORKAROUND: decode_header doesn't work unless there's whitespace
    # around the encoded string (see http://bugs.python.org/issue1079)
    val = email.utils.ecre.sub(' \g<0> ', val) # Workaround: add whitespace
    val = val.strip('"') # remove quotes
    return ''.join(f[0].decode(f[1] or 'us-ascii') for f in decode_header(val))

class BugzillaBase(object):
    '''An object which represents the data and methods exported by a Bugzilla
    instance. Uses xmlrpclib to do its thing. You'll want to create one thusly:
    bz=Bugzilla(url='https://bugzilla.redhat.com/xmlrpc.cgi',user=u,password=p)

    You can get authentication cookies by calling the login() method. These
    cookies will be stored in a MozillaCookieJar-style file specified by the
    'cookiefile' attribute (which defaults to ~/.bugzillacookies). Once you
    get cookies this way, you will be considered logged in until the cookie
    expires.

    You may also specify 'user' and 'password' in a bugzillarc file, either
    /etc/bugzillarc or ~/.bugzillarc. The latter will override the former.
    The format works like this:
      [bugzilla.yoursite.com]
      user = username
      password = password
    You can also use the [DEFAULT] section to set defaults that apply to
    any site without a specific section of its own.
    Be sure to set appropriate permissions on bugzillarc if you choose to
    store your password in it!

    This is an abstract class; it must be implemented by a concrete subclass
    which actually connects the methods provided here to the appropriate
    methods on the bugzilla instance.

    :kwarg url: base url for the bugzilla instance
    :kwarg user: usename to connect with
    :kwarg password: password for the connecting user
    :kwarg cookiefile: Location to save the session cookies so you don't have
        to keep giving the library your username and password.  This defaults
        to ~/.bugzillacookies.  If set to None, the library won't save the
        cookies persistently.
    '''
    def __init__(self, url=None, user=None, password=None,
            cookiefile=os.path.expanduser('~/.bugzillacookies')):
        # Settings the user might want to tweak
        self.user       = user or ''
        self.password   = password or ''
        self.url        = ''

        # We just want to make sure the logic when setting the cookiefile
        # property will initialize the other values
        if cookiefile:
            self._cookiefile = None
        else:
            self._cookiefile = True
        self.cookiefile = cookiefile

        self.user_agent = user_agent
        self.logged_in  = False
        # Bugzilla object state info that users shouldn't mess with
        self.init_private_data()
        if url:
            self.connect(url)

    def init_private_data(self):
        '''initialize private variables used by this bugzilla instance.'''
        self._proxy      = None
        self._transport  = None
        self._opener     = None
        self._querydata  = None
        self._querydefaults = None
        self._products   = None
        self._bugfields  = None
        self._components = dict()
        self._components_details = dict()

    #---- Methods for establishing bugzilla connection and logging in

    def _getcookiefile(self):
        '''cookiefile is the file that bugzilla session cookies are loaded
        and saved from.
        '''
        return self._cookiefile

    def _loadcookies(self, cj):
        """Load cookies from self._cookiefile

        It first tries to use the existing cookiejar object. If it fails, it
        falls back to MozillaCookieJar.

        Returns the CookieJar object used to load the file.
        """
        try:
            cj.load(self._cookiefile)
        except cookielib.LoadError, le:
            cj = cookielib.MozillaCookieJar(self._cookiefile)
            cj.load(self._cookiefile)

        return cj

    def _setcookiefile(self, cookiefile):
        if cookiefile == self._cookiefile:
            # no need to do anything if they're already the same
            return
        del self.cookiefile
        self._cookiefile = cookiefile

        # default. May be overwritten by _loadcookies()
        cj = cookielib.LWPCookieJar(self._cookiefile)

        if not self._cookiefile:
            # Create a temporary cookie file
            tmpfile = tempfile.NamedTemporaryFile(prefix="python-bugzilla.")
            self._cookiefile = tmpfile.name
            # NOTE: tmpfile only exists as long as we have a reference to it!
            self._cookiefobj = tmpfile
            try:
                cj.save(self._cookiefile)
            except Exception, e:
                log.warn("Couldn't initialize temporary cookiefile%s: %s" %
                        (self._cookiefile, str(e)))
        else:
            if os.path.exists(self._cookiefile):
                cj = self._loadcookies(cj)
            else:
                # Create an empty cookiefile that's only readable by this user
                old_umask = os.umask(0077)
                try:
                    cj.save(self._cookiefile)
                except Exception, e:
                    log.error("Couldn't initialize cookiefile %s: %s" %
                            (self._cookiefile, str(e)))
                os.umask(old_umask)

        self._cookiejar = cj
        self._cookiejar.filename = self._cookiefile

    def _delcookiefile(self):
        self._cookiefile = None
        self._cookiefobj = None # makes NamedTemporaryFile delete itself
        self._cookiejar = None

    cookiefile = property(_getcookiefile, _setcookiefile, _delcookiefile)

    def initcookiefile(self, cookiefile=None):
        '''Deprecated: Set self.cookiefile instead. It's a property that will
        take care of these details.

        Read the given (Mozilla-style) cookie file and fill in the
        cookiejar, allowing us to use saved credentials to access Bugzilla.

        :kwarg cookiefile: Location to save the session cookies so you don't
            have to keep giving the library your username and password.  This
            defaults to ~/.bugzillacookies.
        '''
        if not cookiefile:
            cookiefile = os.path.expanduser('~/.bugzillacookies')
        self.cookiefile = cookiefile

    configpath = ['/etc/bugzillarc','~/.bugzillarc']
    def readconfig(self,configpath=None):
        '''Read bugzillarc file(s) into memory.'''
        import ConfigParser
        if not configpath:
            configpath = self.configpath
        configpath = [os.path.expanduser(p) for p in configpath]
        c = ConfigParser.SafeConfigParser()
        r = c.read(configpath)
        if not r:
            return
        # See if we have a config section that matches this url.
        section = ""
        # Substring match - prefer the longest match found
        log.debug("Searching for config section matching %s" % self.url)
        for s in sorted(c.sections(), lambda a,b: cmp(len(a),len(b)) or cmp(a,b)):
            if s in self.url:
                log.debug("Found matching section: %s" % s)
                section = s
        if not section:
            return
        for k,v in c.items(section):
            if k in ('user','password'):
                log.debug("Setting '%s' from configfile" % k)
                setattr(self,k,v)

    def connect(self,url):
        '''Connect to the bugzilla instance with the given url.

        This will also read any available config files (see readconfig()),
        which may set 'user' and 'password'.

        If 'user' and 'password' are both set, we'll run login(). Otherwise
        you'll have to login() yourself before some methods will work.
        '''
        # Set up the transport
        if url.startswith('https'):
            self._transport = SafeCookieTransport()
        else:
            self._transport = CookieTransport()
        self._transport.user_agent = self.user_agent
        self._transport.cookiejar = self._cookiejar
        # Set up the proxy, using the transport
        self._proxy = xmlrpclib.ServerProxy(url,self._transport)
        # Set up the urllib2 opener (using the same cookiejar)
        handler = urllib2.HTTPCookieProcessor(self._cookiejar)
        self._opener = urllib2.build_opener(handler)
        self._opener.addheaders = [('User-agent',self.user_agent)]
        self.url = url
        self.readconfig() # we've changed URLs - reload config
        if (self.user and self.password):
            log.info("user and password present - doing login()")
            self.login()

    def disconnect(self):
        '''Disconnect from the given bugzilla instance.'''
        self.init_private_data() # clears all the connection state

    # Note that the bugzilla methods will ignore an empty user/password if you
    # send authentication info as a cookie in the request headers. So it's
    # OK if we keep sending empty / bogus login info in other methods.
    def _login(self,user,password):
        '''IMPLEMENT ME: backend login method'''
        raise NotImplementedError

    def login(self,user=None,password=None):
        '''Attempt to log in using the given username and password. Subsequent
        method calls will use this username and password. Returns False if
        login fails, otherwise returns some kind of login info - typically
        either a numeric userid, or a dict of user info. It also sets the
        logged_in attribute to True, if successful.

        If user is not set, the value of Bugzilla.user will be used. If *that*
        is not set, ValueError will be raised.

        This method will be called implicitly at the end of connect() if user
        and password are both set. So under most circumstances you won't need
        to call this yourself.
        '''
        if user:
            self.user = user
        if password:
            self.password = password

        if not self.user:
            raise ValueError, "missing username"
        if not self.password:
            raise ValueError, "missing password"

        try:
            r = self._login(self.user,self.password)
            self.logged_in = True
            log.info("login successful - dropping password from memory")
            self.password = ''
        except xmlrpclib.Fault, f:
            r = False
        return r

    def _logout(self):
        '''IMPLEMENT ME: backend login method'''
        raise NotImplementedError

    def logout(self):
        '''Log out of bugzilla. Drops server connection and user info, and
        destroys authentication cookies.'''
        self._logout()
        self.disconnect()
        self.user = ''
        self.password = ''
        self.logged_in  = False

    #---- Methods and properties with basic bugzilla info

    def _getbugfields(self):
        '''IMPLEMENT ME: Get bugfields from Bugzilla.'''
        raise NotImplementedError
    def _getqueryinfo(self):
        '''IMPLEMENT ME: Get queryinfo from Bugzilla.'''
        raise NotImplementedError

    def getbugfields(self,force_refresh=False):
        '''Calls getBugFields, which returns a list of fields in each bug
        for this bugzilla instance. This can be used to set the list of attrs
        on the Bug object.'''
        if force_refresh or not self._bugfields:
            try:
                self._bugfields = self._getbugfields()
            except xmlrpclib.Fault, f:
                if f.faultCode == 'Client':
                    # okay, this instance doesn't have getbugfields. fine.
                    self._bugfields = []
                else:
                    # something bad actually happened on the server. blow up.
                    raise f

        return self._bugfields
    bugfields = property(fget=lambda self: self.getbugfields(),
                         fdel=lambda self: setattr(self,'_bugfields',None))

    def getqueryinfo(self,force_refresh=False):
        '''Calls getQueryInfo, which returns a (quite large!) structure that
        contains all of the query data and query defaults for the bugzilla
        instance. Since this is a weighty call - takes a good 5-10sec on
        bugzilla.redhat.com - we load the info in this private method and the
        user instead plays with the querydata and querydefaults attributes of
        the bugzilla object.'''
        # Only fetch the data if we don't already have it, or are forced to
        if force_refresh or not (self._querydata and self._querydefaults):
            (self._querydata, self._querydefaults) = self._getqueryinfo()
            # TODO: map _querydata to a dict, as with _components_details?
        return (self._querydata, self._querydefaults)
    # Set querydata and querydefaults as properties so they auto-create
    # themselves when touched by a user. This bit was lifted from YumBase,
    # because skvidal is much smarter than I am.
    querydata = property(fget=lambda self: self.getqueryinfo()[0],
                         fdel=lambda self: setattr(self,"_querydata",None))
    querydefaults = property(fget=lambda self: self.getqueryinfo()[1],
                         fdel=lambda self: setattr(self,"_querydefaults",None))

    #---- Methods for retrieving Products

    def _getproducts(self):
        '''IMPLEMENT ME: Get product info from Bugzilla.'''
        raise NotImplementedError

    def getproducts(self,force_refresh=False):
        '''Get product data: names, descriptions, etc.
        The data varies between Bugzilla versions but the basic format is a
        list of dicts, where the dicts will have at least the following keys:
        {'id':1,'name':"Some Product",'description':"This is a product"}

        Any method that requires a 'product' can be given either the
        id or the name.'''
        if force_refresh or not self._products:
            self._products = self._getproducts()
        return self._products
    # Bugzilla.products is a property - we cache the product list on the first
    # call and return it for each subsequent call.
    products = property(fget=lambda self: self.getproducts(),
                        fdel=lambda self: setattr(self,'_products',None))
    def _product_id_to_name(self,productid):
        '''Convert a product ID (int) to a product name (str).'''
        # This will auto-create the 'products' list
        for p in self.products:
            if p['id'] == productid:
                return p['name']
        raise ValueError, 'No product with id #%i' % productid
    def _product_name_to_id(self,product):
        '''Convert a product name (str) to a product ID (int).'''
        for p in self.products:
            if p['name'] == product:
                return p['id']
        raise ValueError, 'No product named "%s"' % product

    #---- Methods for retrieving Components

    def _getcomponentsdetails(self,product):
        '''IMPLEMENT ME: get component details for a product'''
        raise NotImplementedError
    def _getcomponents(self,product):
        '''IMPLEMENT ME: Get component dict for a product'''
        raise NotImplementedError
    def _addcomponent(self,data):
        '''IMPLEMENT ME: Add a component'''
        raise NotImplementedError
    def _editcomponent(self,data):
        '''IMPLEMENT ME: Edit a component'''
        raise NotImplementedError
    def getcomponents(self,product,force_refresh=False):
        '''Return a dict of components:descriptions for the given product.'''
        if force_refresh or product not in self._components:
            self._components[product] = self._getcomponents(product)
        return self._components[product]
    # TODO - add a .components property that acts like a dict?

    def getcomponentsdetails(self,product,force_refresh=False):
        '''Returns a dict of dicts, containing detailed component information
        for the given product. The keys of the dict are component names. For
        each component, the value is a dict with the following keys:
        description, initialowner, initialqacontact, initialcclist'''
        # XXX inconsistent: we don't do this list->dict mapping with querydata
        if force_refresh or product not in self._components_details:
            clist = self._getcomponentsdetails(product)
            cdict = dict()
            for item in clist:
                name = item['component']
                del item['component']
                cdict[name] = item
            self._components_details[product] = cdict
        return self._components_details[product]
    def getcomponentdetails(self,product,component,force_refresh=False):
        '''Get details for a single component. Returns a dict with the
        following keys:
        description, initialowner, initialqacontact, initialcclist'''
        d = self.getcomponentsdetails(product,force_refresh)
        return d[component]
    def addcomponent(self,data):
        '''A method to create a component in Bugzilla. Takes a dict, with the
        following elements:

        product: The product to create the component in
        component: The name of the component to create
        initialowner: The bugzilla login (email address) of the initial owner
        of the component
        initialqacontact: The bugzilla login of the initial QA contact
        initialcclist: The initial list of users to be CC'ed on new bugs for
        the component.
        desription: A one sentence summary of the component

        product, component, description and initalowner are mandatory.
        '''
        self._addcomponent(data)
    def editcomponent(self,data):
        '''A method to edit a component in Bugzilla. Takes a dict, with
            mandatory elements of product. component, and initialowner.
            All other elements are optional and use the same names as the
            addcomponent() method.'''
        # FIXME - initialowner is mandatory for some reason now. Toshio
        # following up with dkl as to why.
        self._editcomponent(data)

    #---- Methods for reading bugs and bug info

    def _getbug(self,id):
        '''IMPLEMENT ME: Return a dict of full bug info for the given bug id'''
        raise NotImplementedError
    def _getbugs(self,idlist):
        '''IMPLEMENT ME: Return a list of full bug dicts, one for each of the
        given bug ids'''
        raise NotImplementedError
    def _getbugsimple(self,id):
        '''IMPLEMENT ME: Return a short dict of simple bug info for the given
        bug id'''
        raise NotImplementedError
    def _getbugssimple(self,idlist):
        '''IMPLEMENT ME: Return a list of short bug dicts, one for each of the
        given bug ids'''
        raise NotImplementedError
    def _query(self,query):
        '''IMPLEMENT ME: Query bugzilla and return a list of matching bugs.'''
        raise NotImplementedError

    # these return Bug objects
    def getbug(self,id):
        '''Return a Bug object with the full complement of bug data
        already loaded.'''
        log.debug("getbug(%s)" % str(id))
        return _Bug(bugzilla=self,dict=self._getbug(id))
    def getbugsimple(self,id):
        '''Return a Bug object given bug id, populated with simple info'''
        return _Bug(bugzilla=self,dict=self._getbugsimple(id))
    def getbugs(self,idlist):
        '''Return a list of Bug objects with the full complement of bug data
        already loaded. If there's a problem getting the data for a given id,
        the corresponding item in the returned list will be None.'''
        return [(b and _Bug(bugzilla=self,dict=b)) or None for b in self._getbugs(idlist)]
    def getbugssimple(self,idlist):
        '''Return a list of Bug objects for the given bug ids, populated with
        simple info. As with getbugs(), if there's a problem getting the data
        for a given bug ID, the corresponding item in the returned list will
        be None.'''
        return [(b and _Bug(bugzilla=self,dict=b)) or None for b in self._getbugssimple(idlist)]
    def query(self,query):
        '''Query bugzilla and return a list of matching bugs.
        query must be a dict with fields like those in in querydata['fields'].
        Returns a list of Bug objects.
        Also see the _query() method for details about the underlying
        implementation.
        '''
        r = self._query(query)
        return [_Bug(bugzilla=self,dict=b) for b in r['bugs']]

    def simplequery(self,product,version='',component='',string='',matchtype='allwordssubstr'):
        '''Convenience method - query for bugs filed against the given
        product, version, and component whose comments match the given string.
        matchtype specifies the type of match to be done. matchtype may be
        any of the types listed in querydefaults['long_desc_type_list'], e.g.:
        ['allwordssubstr','anywordssubstr','substring','casesubstring',
         'allwords','anywords','regexp','notregexp']
        Return value is the same as with query().
        '''
        q = {'product':product,'version':version,'component':component,
             'long_desc':string,'long_desc_type':matchtype}
        return self.query(q)

    #---- Methods for modifying existing bugs.

    # Most of these will probably also be available as Bug methods, e.g.:
    # Bugzilla.setstatus(id,status) ->
    #   Bug.setstatus(status): self.bugzilla.setstatus(self.bug_id,status)

    # FIXME inconsistent method signatures
    # FIXME add more comments on proper implementation
    def _addcomment(self,id,comment,private=False,
                   timestamp='',worktime='',bz_gid=''):
        '''IMPLEMENT ME: add a comment to the given bug ID'''
        raise NotImplementedError
    def _setstatus(self,id,status,comment='',private=False,private_in_it=False,nomail=False):
        '''IMPLEMENT ME: Set the status of the given bug ID'''
        raise NotImplementedError
    def _closebug(self,id,resolution,dupeid,fixedin,comment,isprivate,private_in_it,nomail):
        '''IMPLEMENT ME: close the given bug ID'''
        raise NotImplementedError
    def _setassignee(self,id,**data):
        '''IMPLEMENT ME: set the assignee of the given bug ID'''
        raise NotImplementedError
    def _updatedeps(self,id,blocked,dependson,action):
        '''IMPLEMENT ME: update the deps (blocked/dependson) for the given bug.
        blocked, dependson: list of bug ids/aliases
        action: 'add' or 'delete'
        '''
        raise NotImplementedError
    def _updatecc(self,id,cclist,action,comment='',nomail=False):
        '''IMPLEMENT ME: Update the CC list using the action and account list
        specified.
        cclist must be a list (not a tuple!) of addresses.
        action may be 'add', 'delete', or 'overwrite'.
        comment specifies an optional comment to add to the bug.
        if mail is True, email will be generated for this change.
        Note that using 'overwrite' may result in up to three XMLRPC calls
        (fetch list, remove each element, add new elements). Avoid if possible.
        '''
        raise NotImplementedError
    def _updatewhiteboard(self,id,text,which,action,comment,private):
        '''IMPLEMENT ME: Update the whiteboard given by 'which' for the given
        bug. performs the given action (which may be 'append',' prepend', or
        'overwrite') using the given text.'''
        raise NotImplementedError
    def _updateflags(self,id,flags):
        '''Updates the flags associated with a bug report.
        data should be a hash of {'flagname':'value'} pairs, like so:
        {'needinfo':'?','fedora-cvs':'+'}
        You may also add a "nomail":1 item, which will suppress email if set.'''
        raise NotImplementedError

    #---- Methods for working with attachments

    def _attachment_encode(self,fh):
        '''Return the contents of the file-like object fh in a form
        appropriate for attaching to a bug in bugzilla. This is the default
        encoding method, base64.'''
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

    def _attachfile(self,id,**attachdata):
        '''IMPLEMENT ME: attach a file to the given bug.
        attachdata MUST contain the following keys:
            data:        File data, encoded in the bugzilla-preferred format.
                         attachfile() will encode it with _attachment_encode().
            description: Short description of this attachment.
            filename:    Filename for the attachment.
        The following optional keys may also be added:
            comment:   An optional comment about this attachment.
            isprivate: Set to True if the attachment should be marked private.
            ispatch:   Set to True if the attachment is a patch.
            contenttype: The mime-type of the attached file. Defaults to
                         application/octet-stream if not set. NOTE that text
                         files will *not* be viewable in bugzilla unless you
                         remember to set this to text/plain. So remember that!
        Returns (attachment_id,mailresults).
        '''
        raise NotImplementedError

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
        kwargs['data'] = self._attachment_encode(f)
        (attachid, mailresults) = self._attachfile(id,**kwargs)
        return attachid

    def _attachment_uri(self,attachid):
        '''Returns the URI for the given attachment ID.'''
        att_uri = self.url.replace('xmlrpc.cgi','attachment.cgi')
        att_uri = att_uri + '?id=%s' % attachid
        return att_uri

    def openattachment(self,attachid):
        '''Get the contents of the attachment with the given attachment ID.
        Returns a file-like object.'''
        att_uri = self._attachment_uri(attachid)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookiejar))
        att = opener.open(att_uri)
        # RFC 2183 defines the content-disposition header, if you're curious
        disp = att.headers['content-disposition'].split(';')
        disptype = disp.pop(0)
        parms = dict([p.strip().split("=",1) for p in disp])
        # Parameter values can be quoted/encoded as per RFC 2231
        att.name = decode_rfc2231_value(parms['filename'])
        # Hooray, now we have a file-like object with .read() and .name
        return att

    #---- createbug - big complicated call to create a new bug

    # Default list of required fields for createbug.
    # May be overridden by concrete subclasses.
    createbug_required = ('product','component','version','short_desc','comment',
                          'rep_platform','bug_severity','op_sys','bug_file_loc')

    # List of field aliases. If a createbug() call lacks a required field, but
    # a corresponding alias field is present, we'll automatically switch the
    # field name. This lets us avoid having to change the call to match the
    # bugzilla instance quite so much.
    field_aliases = (('summary','short_desc'),
                     ('description','comment'),
                     ('platform','rep_platform'),
                     ('severity','bug_severity'),
                     ('status','bug_status'))

    def _createbug(self,**data):
        '''IMPLEMENT ME: Raw xmlrpc call for createBug()
        Doesn't bother guessing defaults or checking argument validity.
        Returns bug_id'''
        raise NotImplementedError

    def createbug(self,check_args=False,**data):
        '''Create a bug with the given info. Returns a new Bug object.
        data should be given as keyword args - remember that you can also
        populate a dict and call createbug(**dict) to fill in keyword args.
        The arguments are as follows. Note that some are required, some are
        defaulted, and some are completely optional.

        The Bugzilla 3.2 docs say the following:

        "Clients that want to be able to interact uniformly with multiple
        Bugzillas should always set both the params marked Required and those
        marked Defaulted, because some Bugzillas may not have defaults set for
        Defaulted parameters, and then this method will throw an error if you
        don't specify them."

        REQUIRED:
          product: Name of Bugzilla product.
            Ex: Red Hat Enterprise Linux
          component: Name of component in Bugzilla product.
            Ex: anaconda
          version: Version in the list for the Bugzilla product.
            Ex: 4.5
            See querydata['product'][<product>]['versions'] for values.
          summary: One line summary describing the bug report.

        DEFAULTED:
          platform: Hardware type where this bug was experienced.
            Ex: i386
            See querydefaults['rep_platform_list'] for accepted values.
          severity: Bug severity.
            Ex: medium
            See querydefaults['bug_severity_list'] for accepted values.
          priority: Bug priority.
            Ex: medium
            See querydefaults['priority_list'] for accepted values.
          op_sys: Operating system bug occurs on.
            Ex: Linux
            See querydefaults['op_sys_list'] for accepted values.
          description: A detailed description of the bug report.

        OPTIONAL:
          alias: Give the bug a (string) alias name.
            Alias can't be merely numerical.
            Alias can't contain spaces or commas.
            Alias can't be more than 20 chars long.
            Alias has to be unique.
          assigned_to: Bugzilla username to assign this bug to.
          qa_contact: Bugzilla username of QA contact for this bug.
          cc: List of Bugzilla usernames to CC on this bug.
          keywords: List of keywords for the new bug
          status: Status to place the new bug in. Defaults to NEW.

        Important custom fields (used by RH Bugzilla and maybe others):
        DEFAULTED:
          bug_file_loc: URL pointing to additional information for bug report.
            Ex: http://username.fedorapeople.org/logs/crashlog.txt
          reporter: Bugzilla username to use as reporter.
        OPTIONAL:
          blocked: List of bug ids this report blocks.
          dependson: List of bug ids this report depends on.
        '''
        # If we're getting a call that uses an old fieldname, convert it to the
        # new fieldname instead.
        # XXX - emit deprecation warnings here
        for newfield, oldfield in self.field_aliases:
            if newfield in self.createbug_required and newfield not in data \
                    and oldfield in data:
                data[newfield] = data.pop(oldfield)

        # The xmlrpc will raise an error if one of these is missing, but
        # let's try to save a network roundtrip here if possible..
        for i in self.createbug_required:
            if i not in data or not data[i]:
                if i == 'bug_file_loc':
                    data[i] = 'http://'
                else:
                    raise TypeError, "required field missing or empty: '%s'" % i

        # Sort of a chicken-and-egg problem here - check_args will save you a
        # network roundtrip if your op_sys or rep_platform is bad, but at the
        # expense of getting querydefaults, which is.. an added network
        # roundtrip. Basically it's only useful if you're mucking around with
        # createbug() in ipython and you've already loaded querydefaults.
        if check_args:
            if data['op_sys'] not in self.querydefaults['op_sys_list']:
                raise ValueError, "invalid value for op_sys: %s" % data['op_sys']
            if data['rep_platform'] not in self.querydefaults['rep_platform_list']:
                raise ValueError, "invalid value for rep_platform: %s" % data['rep_platform']
        # Actually perform the createbug call.
        # We return a nearly-empty Bug object, which is kind of a bummer 'cuz
        # it'll take another network roundtrip to fill it. We *could* fake it
        # and fill in the blanks with the data given to this method, but the
        # server might modify/add/drop stuff. Then we'd have a Bug object that
        # lied about the actual contents of the database. That would be bad.
        bug_id = self._createbug(**data)
        return _Bug(self,bug_id=bug_id)

    #---- Methods for retrieving Users

    def _getusers(self, ids=None, names=None, match=None):
        '''IMPLEMEMT ME: Get a list of Bugzilla user'''
        raise NotImplementedError
    def _createuser(self, email, name=None, password=None):
        '''IMPLEMEMT ME: Create a Bugzilla user'''
        raise NotImplementedError

    def _updateperms(self,user,action,group):
        '''IMPLEMEMT ME: Update Bugzilla user permissions'''
        raise NotImplementedError
    def _adduser(self,email,name):
        '''IMPLEMENT ME: Add a bugzilla user

        Deprecated.  User _createuser() instead
        '''
        raise NotImplementedError

    ### These return a User Object ###
    def getuser(self, username):
        '''Return a bugzilla User for the given username

        :arg username: The username used in bugzilla.
        :raises xmlrpclib.Fault: Code 51 if the username does not exist
        :returns: User record for the username
        '''
        rawuser = self._getusers(names=[username])['users'][0]
        # Required fields
        userid = rawuser['id']
        name = rawuser['name']
        # Optional fields
        real_name = rawuser.get('real_name', '')
        email = rawuser.get('email', name)
        can_login = rawuser.get('can_login', False)
        return _User(self, userid=userid, real_name=real_name, email=email,
                name=name, can_login=can_login)

    def getusers(self, userlist):
        '''Return a list of Users from bugzilla.

        :userlist: List of usernames to lookup
        :returns: List of User records
        '''
        return [_User(self, userid=rawuser['id'], name=rawuser['name'],
            real_name=rawuser.get('real_name', ''), email=rawuser.get('email', rawuser['name']),
            can_login=rawuser.get('can_login', False))
            for rawuser in self._getusers(names=userlist)['users']]

    def searchusers(self, pattern):
        '''Return a bugzilla User for the given list of patterns

        :arg pattern: List of patterns to match against.
        :returns: List of User records
        '''
        return [_User(self, userid=rawuser['id'], name=rawuser['name'],
            real_name=rawuser.get('real_name', ''), email=rawuser.get('email', rawuser['name']),
            can_login=rawuser.get('can_login', False))
            for rawuser in self._getusers(match=pattern)['users']]

    def createuser(self, email, name='', password=''):
        '''Return a bugzilla User for the given username

        :arg email: The email address to use in bugzilla
        :kwarg name: Real name to associate with the account
        :kwarg password: Password to set for the bugzilla account
        :raises xmlrpclib.Fault: Code 501 if the username already exists
            Code 500 if the email address isn't valid
            Code 502 if the password is too short
            Code 503 if the password is too long
        :return: User record for the username
        '''
        userid = self._createuser(email, name, password)
        return self.getuser(email)

    def updateperms(self,user,action,groups):
        '''A method to update the permissions (group membership) of a bugzilla
        user.  Deprecated.  Use User.updateperms(action, group) instead.

        :arg user: The e-mail address of the user to be acted upon
        :arg action: either add or rem
        :arg groups: list of groups to be added to (i.e. ['fedora_contrib'])
        '''
        self._updateperms(user,action,groups)

    def adduser(self, user, name):
        '''Deprecated: Use createuser() instead.

        A method to create a user in Bugzilla. Takes the following:

        user: The email address of the user to create
        name: The full name of the user to create
        '''
        self._adduser(user, name)

class CookieResponse:
    '''Fake HTTPResponse object that we can fill with headers we got elsewhere.
    We can then pass it to CookieJar.extract_cookies() to make it pull out the
    cookies from the set of headers we have.'''
    def __init__(self,headers):
        self.headers = headers
        #log.debug("CookieResponse() headers = %s" % headers)
    def info(self):
        return self.headers

class CookieTransport(xmlrpclib.Transport):
    '''A subclass of xmlrpclib.Transport that supports cookies.'''
    cookiejar = None
    scheme = 'http'

    # Cribbed from xmlrpclib.Transport.send_user_agent
    def send_cookies(self, connection, cookie_request):
        if self.cookiejar is None:
            log.debug("send_cookies(): creating in-memory cookiejar")
            self.cookiejar = cookielib.CookieJar()
        elif self.cookiejar:
            log.debug("send_cookies(): using existing cookiejar")
            # Let the cookiejar figure out what cookies are appropriate
            log.debug("cookie_request headers currently: %s" % cookie_request.header_items())
            self.cookiejar.add_cookie_header(cookie_request)
            log.debug("cookie_request headers now: %s" % cookie_request.header_items())
            # Pull the cookie headers out of the request object...
            cookielist=list()
            for h,v in cookie_request.header_items():
                if h.startswith('Cookie'):
                    log.debug("sending cookie: %s=%s" % (h,v))
                    cookielist.append([h,v])
            # ...and put them over the connection
            for h,v in cookielist:
                connection.putheader(h,v)
        else:
            log.debug("send_cookies(): cookiejar empty. Nothing to send.")

    # This is the same request() method from python 2.6's xmlrpclib.Transport,
    # with a couple additions noted below
    def request_with_cookies(self, host, handler, request_body, verbose=0):
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        # ADDED: construct the URL and Request object for proper cookie handling
        request_url = "%s://%s%s" % (self.scheme,host,handler)
        log.debug("request_url is %s" % request_url)
        cookie_request  = urllib2.Request(request_url)

        self.send_request(h,handler,request_body)
        self.send_host(h,host)
        self.send_cookies(h,cookie_request) # ADDED. creates cookiejar if None.
        self.send_user_agent(h)
        self.send_content(h,request_body)

        errcode, errmsg, headers = h.getreply()

        # ADDED: parse headers and get cookies here
        cookie_response = CookieResponse(headers)
        # Okay, extract the cookies from the headers
        self.cookiejar.extract_cookies(cookie_response,cookie_request)
        log.debug("cookiejar now contains: %s" % self.cookiejar._cookies)
        # And write back any changes
        if hasattr(self.cookiejar,'save'):
            try:
                self.cookiejar.save(self.cookiejar.filename)
            except Exception, e:
                log.error("Couldn't write cookiefile %s: %s" % \
                        (self.cookiejar.filename,str(e)))

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

    # This is just python 2.7's xmlrpclib.Transport.single_request, with
    # send additions noted below to send cookies along with the request
    def single_request_with_cookies(self, host, handler, request_body, verbose=0):
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        # ADDED: construct the URL and Request object for proper cookie handling
        request_url = "%s://%s%s" % (self.scheme,host,handler)
        log.debug("request_url is %s" % request_url)
        cookie_request  = urllib2.Request(request_url)

        try:
            self.send_request(h,handler,request_body)
            self.send_host(h,host)
            self.send_cookies(h,cookie_request) # ADDED. creates cookiejar if None.
            self.send_user_agent(h)
            self.send_content(h,request_body)

            response = h.getresponse(buffering=True)

            # ADDED: parse headers and get cookies here
            cookie_response = CookieResponse(response.msg)
            # Okay, extract the cookies from the headers
            self.cookiejar.extract_cookies(cookie_response,cookie_request)
            log.debug("cookiejar now contains: %s" % self.cookiejar._cookies)
            # And write back any changes
            if hasattr(self.cookiejar,'save'):
                try:
                    self.cookiejar.save(self.cookiejar.filename)
                except Exception, e:
                    log.error("Couldn't write cookiefile %s: %s" % \
                            (self.cookiejar.filename,str(e)))

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

        #discard any response data and raise exception
        if (response.getheader("content-length", 0)):
            response.read()
        raise xmlrpclib.ProtocolError(
            host + handler,
            response.status, response.reason,
            response.msg,
            )

    # Override the appropriate request method
    if hasattr(xmlrpclib.Transport, 'single_request'):
        single_request = single_request_with_cookies # python 2.7+
    else:
        request = request_with_cookies # python 2.6 and earlier

class SafeCookieTransport(xmlrpclib.SafeTransport,CookieTransport):
    '''SafeTransport subclass that supports cookies.'''
    scheme = 'https'
    # Override the appropriate request method
    if hasattr(xmlrpclib.Transport, 'single_request'):
        single_request = CookieTransport.single_request_with_cookies
    else:
        request = CookieTransport.request_with_cookies

class _User(object):
    '''Container object for a bugzilla User.

    :arg bugzilla: Bugzilla instance that this User belongs to.
    :arg name: name that references a user
    :kwarg userid: id in bugzilla for a user
    :kwarg real_name: User's real name
    :kwarg email: User's email address
    :kwarg can_login: If set True, the user can login
    '''
    def __init__(self, bugzilla, name, userid, real_name=None, email=None,
            can_login=True):
        self.bugzilla = bugzilla
        self.__name = name
        self.__userid = userid
        self.real_name = real_name
        self.__email = email
        self.__can_login = can_login
        # This tells us whether self.name has been changed but not synced to
        # bugzilla
        self._name_dirty = False

    ### Read-only attributes ###

    # We make these properties so that the user cannot set them.  They are
    # unaffected by the update() method so it would be misleading to let them
    # be changed.
    @property
    def userid(self):
        return self.__userid

    @property
    def email(self):
        return self.__email

    @property
    def can_login(self):
        return self.__can_login

    ### name is a key in some methods.  Mark it dirty when we change it ###
    def _name(self):
        return self.__name
    def _set_name(self, value):
        self._name_dirty = True
        self.__name = value
    name = property(_name, _set_name)

    def update(self):
        '''Update Bugzilla with these values.

        :raises xmlrpclib.Fault: Code 304 if you aren't allowed to edit
            the user
        '''
        self._name__dirty = False
        self.bugzilla._update(ids=self.userid, update={'name': self.name,
            'real_name': self.real_name, 'password': self.password})

    def updateperms(self, action, groups):
        '''A method to update the permissions (group membership) of a bugzilla
        user.

        :arg action: either add or rem
        :arg groups: list of groups to be added to (i.e. ['fedora_contrib'])
        '''
        if self._name_dirty:
            raise NeedSyncError('name has been changed.  run update() before'
                    ' updating perms.')
        self.bugzilla._updateperms(self.name, action, groups)

class _Bug(object):
    '''A container object for a bug report. Requires a Bugzilla instance -
    every Bug is on a Bugzilla, obviously.
    Optional keyword args:
        dict=DICT   - populate attributes with the result of a getBug() call
        bug_id=ID   - if dict does not contain bug_id, this is required before
                      you can read any attributes or make modifications to this
                      bug.
        autorefresh - automatically refresh the data in this bug after calling
                      a method that modifies the bug. Defaults to True. You can
                      call refresh() to do this manually.
    '''
    def __init__(self,bugzilla,**kwargs):
        self.bugzilla = bugzilla
        self.autorefresh = True
        if 'dict' in kwargs and kwargs['dict']:
            log.debug("Bug(%s)" % kwargs['dict'].keys())
            self.__dict__.update(kwargs['dict'])
        if 'bug_id' in kwargs:
            log.debug("Bug(%i)" % kwargs['bug_id'])
            setattr(self,'bug_id',kwargs['bug_id'])
        if 'autorefresh' in kwargs:
            self.autorefresh = kwargs['autorefresh']
        # No bug_id? this bug is invalid!
        if not hasattr(self,'bug_id'):
            if hasattr(self,'id'):
                self.bug_id = self.id
            else:
                raise TypeError, "Bug object needs a bug_id"

        self.url = bugzilla.url.replace('xmlrpc.cgi',
                                        'show_bug.cgi?id=%i' % self.bug_id)

        # TODO: set properties for missing bugfields
        # The problem here is that the property doesn't know its own name,
        # otherwise we could just do .refresh() and return __dict__[f] after.
        # basically I need a suicide property that can replace itself after
        # it's called. Or something.
        #for f in bugzilla.bugfields:
        #    if f in self.__dict__: continue
        #    setattr(self,f,property(fget=lambda self: self.refresh()))

    def __str__(self):
        '''Return a simple string representation of this bug

        This is available only for compatibility. Using 'str(bug)' and
        'print bug' is not recommended because of potential encoding issues.
        Please use unicode(bug) where possible.
        '''
        return unicode(self).encode(locale.getpreferredencoding(), 'replace')

    def __unicode__(self):
        '''Return a simple unicode string representation of this bug'''
        # XXX Not really sure why we get short_desc sometimes and
        # short_short_desc other times. I feel like I'm working around
        # a bug here, so keep an eye on this.
        if 'short_short_desc' in self.__dict__:
            desc = self.short_short_desc
        elif 'short_desc' in self.__dict__:
            desc = self.short_desc
        elif 'summary' in self.__dict__:
            desc = self.summary
        else:
            log.warn("Weird; this bug has no summary?")
            desc = "[ERROR: SUMMARY MISSING]"
            log.debug(self.__dict__)
        # Some BZ3 implementations give us an ID instead of a name.
        if 'assigned_to' not in self.__dict__:
            if 'assigned_to_id' in self.__dict__:
                self.assigned_to = self.bugzilla._getuserforid(self.assigned_to_id)
        return u"#%-6s %-10s - %s - %s" % (self.bug_id,self.bug_status,
                                          self.assigned_to,desc)
    def __repr__(self):
        return '<Bug #%i on %s at %#x>' % (self.bug_id,self.bugzilla.url,
                                           id(self))

    def __getattr__(self,name):
        if 'bug_id' in self.__dict__:
            if self.bugzilla.bugfields and name not in self.bugzilla.bugfields:
                # We have a list of fields, and you ain't on it.
                # Check the aliases
                for a in self.bugzilla.field_aliases:
                    if a[0] == name: return getattr(self, a[1])
                    if a[1] == name: return getattr(self, a[0])
                # Not in the aliases. Bail out.
                raise AttributeError, "field %s not in bugzilla.bugfields" % name
            log.debug("Bug %i missing %s - doing refresh()", self.bug_id, name)
            self.refresh()
            if name in self.__dict__:
                return self.__dict__[name]
        raise AttributeError, "Bug object has no attribute '%s'" % name

    def __getstate__(self):
        sd = self.__dict__
        if self.bugzilla: fields = self.bugzilla.bugfields
        else: fields = self.bugfields
        vals = [(k,sd[k]) for k in sd.keys() if k in fields]
        vals.append( ('bugfields', fields) )
        return dict(vals)

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.bugzilla = None

    def refresh(self):
        '''Refresh all the data in this Bug.'''
        if self.bugzilla.bugfields:
            for k in self.bugzilla.bugfields:
                self.__dict__.setdefault(k)
        r = self.bugzilla._getbug(self.bug_id)
        self.__dict__.update(r)

    def reload(self):
        '''An alias for refresh()'''
        self.refresh()

    def setstatus(self,status,comment='',private=False,private_in_it=False,nomail=False):
        '''Update the status for this bug report.
        Valid values for status are listed in querydefaults['bug_status_list']
        Commonly-used values are ASSIGNED, MODIFIED, and NEEDINFO.
        To change bugs to CLOSED, use .close() instead.
        See Bugzilla._setstatus() for details.'''
        self.bugzilla._setstatus(self.bug_id,status,comment,private,private_in_it,nomail)
        # TODO reload bug data here?

    def setassignee(self,assigned_to='',reporter='',qa_contact='',comment=''):
        '''Set any of the assigned_to, reporter, or qa_contact fields to a new
        bugzilla account, with an optional comment, e.g.
        setassignee(reporter='sadguy@brokencomputer.org',
                    assigned_to='wwoods@redhat.com')
        setassignee(qa_contact='wwoods@redhat.com',comment='wwoods QA ftw')
        You must set at least one of the three assignee fields, or this method
        will throw a ValueError.
        Returns [bug_id, mailresults].'''
        if not (assigned_to or reporter or qa_contact):
            # XXX is ValueError the right thing to throw here?
            raise ValueError, "You must set one of assigned_to, reporter, or qa_contact"
        # empty fields are ignored, so it's OK to send 'em
        r = self.bugzilla._setassignee(self.bug_id,assigned_to=assigned_to,
                reporter=reporter,qa_contact=qa_contact,comment=comment)
        # TODO reload bug data here?
        return r
    def addcomment(self,comment,private=False,timestamp='',worktime='',bz_gid=''):
        '''Add the given comment to this bug. Set private to True to mark this
        comment as private. You can also set a timestamp for the comment, in
        "YYYY-MM-DD HH:MM:SS" form. Worktime is undocumented upstream.
        If bz_gid is set, and the entire bug is not already private to that
        group, this comment will be private.'''
        self.bugzilla._addcomment(self.bug_id,comment,private,timestamp,
                                  worktime,bz_gid)
        # TODO reload bug data here?
    def close(self,resolution,dupeid=0,fixedin='',comment='',isprivate=False,private_in_it=False,nomail=False):
        '''Close this bug.
        Valid values for resolution are in bz.querydefaults['resolution_list']
        For bugzilla.redhat.com that's:
        ['NOTABUG','WONTFIX','DEFERRED','WORKSFORME','CURRENTRELEASE',
         'RAWHIDE','ERRATA','DUPLICATE','UPSTREAM','NEXTRELEASE','CANTFIX',
         'INSUFFICIENT_DATA']
        If using DUPLICATE, you need to set dupeid to the ID of the other bug.
        If using WORKSFORME/CURRENTRELEASE/RAWHIDE/ERRATA/UPSTREAM/NEXTRELEASE
          you can (and should) set 'new_fixed_in' to a string representing the
          version that fixes the bug.
        You can optionally add a comment while closing the bug. Set 'isprivate'
          to True if you want that comment to be private.
        If you want to suppress sending out mail for this bug closing, set
          nomail=True.
        '''
        self.bugzilla._closebug(self.bug_id,resolution,dupeid,fixedin,
                                comment,isprivate,private_in_it,nomail)
        # TODO reload bug data here?
    def updateflags(self,flags):
        '''Updates the bugzilla flags.
        The flags values are a hash of {'flagname': 'value'} pairs.
        Each product seems to have different flags available, so this can be
        error-prone unless the error code is understood.
        '''
        self.bugzilla._updateflags(self.bug_id,flags)
        # TODO reload bug data here?
    def _dowhiteboard(self,text,which,action,comment,private):
        '''Actually does the updateWhiteboard call to perform the given action
        (append,prepend,overwrite) with the given text on the given whiteboard
        for the given bug.'''
        self.bugzilla._updatewhiteboard(self.bug_id,text,which,action,comment,private)
        # TODO reload bug data here?

    def getwhiteboard(self,which='status'):
        '''Get the current value of the whiteboard specified by 'which'.
        Known whiteboard names: 'status','internal','devel','qa'.
        Defaults to the 'status' whiteboard.'''
        return getattr(self,"%s_whiteboard" % which)
    def appendwhiteboard(self,text,which='status',comment=None,private=False):
        '''Append the given text (with a space before it) to the given
        whiteboard. Defaults to using status_whiteboard.'''
        self._dowhiteboard(text,which,'append',comment,private)
    def prependwhiteboard(self,text,which='status',comment=None,private=False):
        '''Prepend the given text (with a space following it) to the given
        whiteboard. Defaults to using status_whiteboard.'''
        self._dowhiteboard(text,which,'prepend',comment,private)
    def setwhiteboard(self,text,which='status',comment=None,private=False):
        '''Overwrites the contents of the given whiteboard with the given text.
        Defaults to using status_whiteboard.'''
        self._dowhiteboard(text,which,'overwrite',comment,private)
    def addtag(self,tag,which='status'):
        '''Adds the given tag to the given bug.'''
        whiteboard = self.getwhiteboard(which)
        if whiteboard:
            self.appendwhiteboard(tag,which)
        else:
            self.setwhiteboard(tag,which)
    def gettags(self,which='status'):
        '''Get a list of tags (basically just whitespace-split the given
        whiteboard)'''
        return self.getwhiteboard(which).split()
    def deltag(self,tag,which='status'):
        '''Removes the given tag from the given bug.'''
        tags = self.gettags(which)
        tags.remove(tag)
        self.setwhiteboard(' '.join(tags),which)
    def addcc(self,cclist,comment=''):
        '''Adds the given email addresses to the CC list for this bug.
        cclist: list of email addresses (strings)
        comment: optional comment to add to the bug'''
        self.bugzilla._updatecc(self.bug_id,cclist,'add',comment)
    def deletecc(self,cclist,comment=''):
        '''Removes the given email addresses from the CC list for this bug.'''
        self.bugzilla._updatecc(self.bug_id,cclist,'delete',comment)

    def get_flag_type(self, name):
        """Return flag_type information for a specific flag"""

        #XXX: make a "flag index" dictionary instead of walking the
        #     flag_types list every time?

        for t in self.flag_types:
            if t['name'] == name:
                return t

        # not found
        return None

    def get_flags(self, name):
        """Return flag value information for a specific flag
        """
        ft = self.get_flag_type(name)
        if not ft:
            return None

        return ft['flags']

    def get_flag_status(self, name):
        """Return a flag 'status' field

        This method works only for simple flags that have only a 'status' field
        with no "requestee" info, and no multiple values. For more complex
        flags, use get_flags() to get extended flag value information.
        """
        f = self.get_flags(name)
        if not f:
            return None

        # This method works only for simple flags that have only one
        # value set.
        assert len(f) <= 1

        return f[0]['status']

# Backwards compatibility
Bug = _Bug

# TODO: attach(file), getflag(), setflag()
# TODO: add a sync() method that writes the changed data in the Bug object
# back to Bugzilla?
