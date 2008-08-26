# base.py - the base classes etc. for a Python interface to bugzilla
#
# Copyright (C) 2007,2008 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import xmlrpclib, urllib2, cookielib
import os.path, base64, copy
import logging
log = logging.getLogger('bugzilla')

version = '0.4'
user_agent = 'Python-urllib2/%s bugzilla.py/%s' % \
        (urllib2.__version__,version)

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

    The methods which start with a single underscore are thin wrappers around
    xmlrpc calls; those should be safe for multicall usage.

    This is an abstract class; it must be implemented by a concrete subclass
    which actually connects the methods provided here to the appropriate
    methods on the bugzilla instance.
    '''
    def __init__(self,**kwargs):
        # Settings the user might want to tweak
        self.user       = ''
        self.password   = ''
        self.url        = ''
        self.cookiefile = os.path.expanduser('~/.bugzillacookies')
        self.user_agent = user_agent
        self.logged_in  = False
        # Bugzilla object state info that users shouldn't mess with
        self.init_private_data()
        if 'url' in kwargs:
            self.connect(kwargs['url'])
        if 'user' in kwargs:
            self.user = kwargs['user']
        if 'password' in kwargs:
            self.password = kwargs['password']

    def init_private_data(self):
        '''initialize private variables used by this bugzilla instance.'''
        self._cookiejar  = None
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

    def initcookiefile(self,cookiefile=None):
        '''Read the given (Mozilla-style) cookie file and fill in the
        cookiejar, allowing us to use saved credentials to access Bugzilla.
        If no file is given, self.cookiefile will be used.'''
        if cookiefile: 
            self.cookiefile = cookiefile
        cj = cookielib.MozillaCookieJar(self.cookiefile)
        if os.path.exists(self.cookiefile):
            cj.load()
        self._cookiejar = cj
        self._cookiejar.filename = self.cookiefile

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
        self.initcookiefile() # sets _cookiejar
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

    # FIXME MultiCall support is a RHism, so this should move into rhbugzilla
    def _multicall(self):
        '''This returns kind of a mash-up of the Bugzilla object and the 
        xmlrpclib.MultiCall object. Methods you call on this object will be added
        to the MultiCall queue, but they will return None. When you're ready, call
        the run() method and all the methods in the queue will be run and the
        results of each will be returned in a list. So, for example:

        mc = bz._multicall()
        mc._getbug(1)
        mc._getbug(1337)
        mc._query({'component':'glibc','product':'Fedora','version':'devel'})
        (bug1, bug1337, queryresult) = mc.run()
    
        Note that you should only use the raw xmlrpc calls (mostly the methods
        starting with an underscore). Normal getbug(), for example, tries to
        return a Bug object, but with the multicall object it'll end up empty
        and, therefore, useless.

        Further note that run() returns a list of raw xmlrpc results; you'll
        need to wrap the output in Bug objects yourself if you're doing that
        kind of thing. For example, Bugzilla.getbugs() could be implemented:

        mc = self._multicall()
        for id in idlist:
            mc._getbug(id)
        rawlist = mc.run()
        return [Bug(self,dict=b) for b in rawlist]
        '''
        mc = copy.copy(self)
        mc._proxy = xmlrpclib.MultiCall(self._proxy)
        def run(): return mc._proxy().results
        mc.run = run
        return mc

    def _getbugfields(self):
        '''IMPLEMENT ME: Get bugfields from Bugzilla.'''
        raise NotImplementedError
    def _getqueryinfo(self):
        '''IMPLEMENT ME: Get queryinfo from Bugzilla.'''
        raise NotImplementedError
    def _getproducts(self):
        '''IMPLEMENT ME: Get product info from Bugzilla.'''
        raise NotImplementedError
    def _getcomponentsdetails(self,product):
        '''IMPLEMENT ME: get component details for a product'''
        raise NotImplementedError
    def _getcomponents(self,product):
        '''IMPLEMENT ME: Get component dict for a product'''
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
    def _product_name_to_id(self,product):
        '''Convert a product name (str) to a product ID (int).'''
        for p in self.products:
            if p['name'] == product:
                return p['id']

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

    def _get_info(self,product=None):
        '''This is a convenience method that does getqueryinfo, getproducts,
        and (optionally) getcomponents in one big fat multicall. This is a bit
        faster than calling them all separately.
        
        If you're doing interactive stuff you should call this, with the
        appropriate product name, after connecting to Bugzilla. This will
        cache all the info for you and save you an ugly delay later on.'''
        mc = self._multicall()
        mc._getqueryinfo()
        mc._getproducts()
        mc._getbugfields()
        if product:
            mc._getcomponents(product)
            mc._getcomponentsdetails(product)
        r = mc.run()
        (self._querydata,self._querydefaults) = r.pop(0)
        self._products = r.pop(0)
        self._bugfields = r.pop(0)
        if product:
            self._components[product] = r.pop(0)
            self._components_details[product] = r.pop(0)

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
        log.debug("getbug(%i)" % id)
        return Bug(bugzilla=self,dict=self._getbug(id))
    def getbugsimple(self,id):
        '''Return a Bug object given bug id, populated with simple info'''
        return Bug(bugzilla=self,dict=self._getbugsimple(id))
    def getbugs(self,idlist):
        '''Return a list of Bug objects with the full complement of bug data
        already loaded. If there's a problem getting the data for a given id,
        the corresponding item in the returned list will be None.'''
        return [(b and Bug(bugzilla=self,dict=b)) or None for b in self._getbugs(idlist)]
    def getbugssimple(self,idlist):
        '''Return a list of Bug objects for the given bug ids, populated with
        simple info. As with getbugs(), if there's a problem getting the data
        for a given bug ID, the corresponding item in the returned list will
        be None.'''
        return [(b and Bug(bugzilla=self,dict=b)) or None for b in self._getbugssimple(idlist)]
    def query(self,query):
        '''Query bugzilla and return a list of matching bugs.
        query must be a dict with fields like those in in querydata['fields'].
        Returns a list of Bug objects.
        Also see the _query() method for details about the underlying
        implementation.
        '''
        r = self._query(query)
        return [Bug(bugzilla=self,dict=b) for b in r['bugs']]

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
    def _updatewhiteboard(self,id,text,which,action):
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
        (attachid, mailresults) = self._attachfile(id,kwargs)
        return attachid

    def _attachment_uri(self,attachid):
        '''Returns the URI for the given attachment ID.'''
        att_uri = self._url.replace('xmlrpc.cgi','attachment.cgi')
        att_uri = att_uri + '?%i' % attachid
        return att_uri

    def openattachment(self,attachid):
        '''Get the contents of the attachment with the given attachment ID.
        Returns a file-like object.'''
        att_uri = self._attachment_uri(attachid)
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

    #---- createbug - big complicated call to create a new bug

    # Default list of required fields for createbug
    createbug_required = ('product','component','version','short_desc','comment',
                          'rep_platform','bug_severity','op_sys','bug_file_loc')

    def _createbug(self,**data):
        '''IMPLEMENT ME: Raw xmlrpc call for createBug() 
        Doesn't bother guessing defaults or checking argument validity. 
        Returns bug_id'''
        raise NotImplementedError

    def createbug(self,check_args=False,**data):
        '''Create a bug with the given info. Returns a new Bug object.
        data should be given as keyword args - remember that you can also
        populate a dict and call createbug(**dict) to fill in keyword args.
        The arguments are as follows. Note that some are optional and some
        are required. 

        "product" => "<Product Name>",
            # REQUIRED Name of Bugzilla product. 
            # Ex: Red Hat Enterprise Linux
        "component" => "<Component Name>",
            # REQUIRED Name of component in Bugzilla product. 
            # Ex: anaconda
        "version" => "<Version of Product>",
            # REQUIRED Version in the list for the Bugzilla product. 
            # Ex: 4.5
            # versions are listed in querydata['product'][<product>]['versions']
        "rep_platform" => "<Platform>",
            # REQUIRED Valid architecture from the rep_platform list. 
            # Ex: i386
            # See querydefaults['rep_platform_list'] for accepted values.
        "bug_severity" => "medium",
            # REQUIRED Valid severity from the list of severities.
            # See querydefaults['bug_severity_list'] for accepted values.
        "op_sys" => "Linux",
            # REQUIRED Operating system bug occurs on. 
            # See querydefaults['op_sys_list'] for accepted values.
        "bug_file_loc" => "http://",
            # REQUIRED URL to additional information for bug report. 
            # Ex: http://people.redhat.com/dkl
        "short_desc" => "<Brief text about bug>",
            # REQUIRED One line summary describing the bug report.
        "comment" => "<More Detailed Description>",
            # REQUIRED A detail descript about the bug report.

        "alias" => "<Bug Alias>",
            # OPTIONAL Will give the bug an alias name.
            # Alias can't be merely numerical.
            # Alias can't contain spaces or commas.
            # Alias can't be more than 20 chars long.
            # Alias has to be unique.
        "assigned_to" => "<Bugzilla Account>",          
            # OPTIONAL Will be determined by component owner otherwise.
        "reporter" => "<Bugzilla Account>",
            # OPTIONAL Will use current login if blank.
        "qa_contact" => "<Bugzilla Account>",
            # OPTIONAL Will be determined by component qa_contact otherwise.
        "cc" => "<Comma/Space separated list>",
            # OPTIONAL Space or Comma separated list of Bugzilla accounts.
        "priority" => "urgent",
            # OPTIONAL Valid priority from the list of priorities.
            # Ex: medium
            # See querydefaults['priority_list'] for accepted values.
        "bug_status" => 'NEW',
            # OPTIONAL Status to place the new bug in. 
            # Default: NEW
        "blocked" => '',
            # OPTIONAL Comma or space separate list of bug id's 
            # this report blocks.
        "dependson" => '',
            # OPTIONAL Comma or space separate list of bug id's 
            # this report depends on.
        '''
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
        return Bug(self,bug_id=bug_id)
        # Trivia: this method has ~5.8 lines of comment per line of code. Yow!

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

    # This is the same request() method from xmlrpclib.Transport,
    # with a couple additions noted below
    def request(self, host, handler, request_body, verbose=0):
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
            except e:
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

class SafeCookieTransport(xmlrpclib.SafeTransport,CookieTransport):
    '''SafeTransport subclass that supports cookies.'''
    scheme = 'https'
    request = CookieTransport.request

class Bug(object):
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
        '''Return a simple string representation of this bug'''
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
        return "#%-6s %-10s - %s - %s" % (self.bug_id,self.bug_status,
                                          self.assigned_to,desc)
    def __repr__(self):
        return '<Bug #%i on %s at %#x>' % (self.bug_id,self.bugzilla.url,
                                           id(self))

    def __getattr__(self,name):
        if 'bug_id' in self.__dict__:
            if self.bugzilla.bugfields and name not in self.bugzilla.bugfields:
                # We have a list of fields, and you ain't on it. Bail out.
                raise AttributeError, "field %s not in bugzilla.bugfields" % name
            #print "Bug %i missing %s - loading" % (self.bug_id,name)
            self.refresh()
            if name in self.__dict__:
                return self.__dict__[name]
        raise AttributeError, "Bug object has no attribute '%s'" % name

    def refresh(self):
        '''Refresh all the data in this Bug.'''
        r = self.bugzilla._getbug(self.bug_id)
        self.__dict__.update(r)

    def reload(self): 
        '''An alias for reload()'''
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
    def _dowhiteboard(self,text,which,action):
        '''Actually does the updateWhiteboard call to perform the given action
        (append,prepend,overwrite) with the given text on the given whiteboard
        for the given bug.'''
        self.bugzilla._updatewhiteboard(self.bug_id,text,which,action)
        # TODO reload bug data here?

    def getwhiteboard(self,which='status'):
        '''Get the current value of the whiteboard specified by 'which'.
        Known whiteboard names: 'status','internal','devel','qa'.
        Defaults to the 'status' whiteboard.'''
        return getattr(self,"%s_whiteboard" % which)
    def appendwhiteboard(self,text,which='status'):
        '''Append the given text (with a space before it) to the given 
        whiteboard. Defaults to using status_whiteboard.'''
        self._dowhiteboard(text,which,'append')
    def prependwhiteboard(self,text,which='status'):
        '''Prepend the given text (with a space following it) to the given
        whiteboard. Defaults to using status_whiteboard.'''
        self._dowhiteboard(text,which,'prepend')
    def setwhiteboard(self,text,which='status'):
        '''Overwrites the contents of the given whiteboard with the given text.
        Defaults to using status_whiteboard.'''
        self._dowhiteboard(text,which,'overwrite')
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
        self.bugzilla.updatecc(self.bug_id,cclist,'add',comment)
    def deletecc(self,cclist,comment=''):
        '''Removes the given email addresses from the CC list for this bug.'''
        self.bugzilla.updatecc(self.bug_id,cclist,'delete',comment)
# TODO: attach(file), getflag(), setflag()
# TODO: add a sync() method that writes the changed data in the Bug object
# back to Bugzilla?
