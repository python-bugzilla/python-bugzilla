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

import base64
import cookielib
import os
import tempfile
import urllib2
import xmlrpclib

from bugzilla import __version__, log
from bugzilla.bug import _Bug, _User
from bugzilla.cookies import CookieTransport, SafeCookieTransport

# Backwards compatibility
Bug = _Bug


def _decode_rfc2231_value(val):
    # BUG WORKAROUND: decode_header doesn't work unless there's whitespace
    # around the encoded string (see http://bugs.python.org/issue1079)
    from email import utils
    from email import header

    val = utils.ecre.sub(' \g<0> ', val)
    val = val.strip('"')
    return ''.join(f[0].decode(f[1] or 'us-ascii')
                   for f in header.decode_header(val))


class BugzillaError(Exception):
    '''Error raised in the Bugzilla client code.'''
    pass


class BugzillaBase(object):
    '''An object which represents the data and methods exported by a Bugzilla
    instance. Uses xmlrpclib to do its thing. You'll want to create one thusly:
    bz=Bugzilla(url='https://bugzilla.redhat.com/xmlrpc.cgi',
                user=u, password=p)

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
    bz_ver_major = 0
    bz_ver_minor = 0

    # This is the class API version
    version = "0.1"

    @staticmethod
    def url_to_query(url):
        '''
        Given a big huge bugzilla query URL, returns a query dict that can
        be passed along to the Bugzilla.query() method.
        '''
        import urlparse

        q = {}
        (ignore, ignore, path,
         ignore, query, ignore) = urlparse.urlparse(url)

        if os.path.basename(path) in ('buglist.cgi', 'query.cgi'):
            for (k, v) in urlparse.parse_qsl(query):
                if k not in q:
                    q[k] = v
                elif isinstance(q[k], list):
                    q[k].append(v)
            else:
                oldv = q[k]
                q[k] = [oldv, v]
        return q


    def __init__(self, url=None, user=None, password=None,
            cookiefile=os.path.expanduser('~/.bugzillacookies')):
        # Settings the user might want to tweak
        self.user = user or ''
        self.password = password or ''
        self.url = ''

        self._cookiefobj = None
        self._cookiejar = None
        self._cookiefile = -1
        self.cookiefile = cookiefile

        self.logged_in = False

        # Bugzilla object state info that users shouldn't mess with
        self._proxy = None
        self._transport = None
        self._opener = None
        self._querydata = None
        self._querydefaults = None
        self._products = None
        self._bugfields = None
        self._components = {}
        self._components_details = {}
        self._init_private_data()

        if url:
            self.connect(url)

    def _init_private_data(self):
        '''initialize private variables used by this bugzilla instance.'''
        self._proxy = None
        self._transport = None
        self._opener = None
        self._querydata = None
        self._querydefaults = None
        self._products = None
        self._bugfields = None
        self._components = {}
        self._components_details = {}

    def _get_user_agent(self):
        ret = ('Python-urllib2/%s bugzilla.py/%s %s/%s' %
               (urllib2.__version__, __version__,
                str(self.__class__.__name__), self.version))
        return ret
    user_agent = property(_get_user_agent)


    ###################
    # Private helpers #
    ###################

    def _check_version(self, major, minor):
        """
        Check if the detected bugzilla version is >= passed major/minor pair.
        """
        if major < self.bz_ver_major:
            return True
        if (major == self.bz_ver_major and minor <= self.bz_ver_minor):
            return True
        return False

    def _listify(self, val):
        if val is None:
            return val
        if type(val) is list:
            return val
        return [val]

    def _product_id_to_name(self, productid):
        '''Convert a product ID (int) to a product name (str).'''
        for p in self.products:
            if p['id'] == productid:
                return p['name']
        raise ValueError('No product with id #%i' % productid)

    def _product_name_to_id(self, product):
        '''Convert a product name (str) to a product ID (int).'''
        for p in self.products:
            if p['name'] == product:
                return p['id']
        raise ValueError('No product named "%s"' % product)


    ###################
    # Cookie handling #
    ###################

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
        except cookielib.LoadError:
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
        self._cookiefobj = None
        self._cookiejar = None

    cookiefile = property(_getcookiefile, _setcookiefile, _delcookiefile)


    #############################
    # Login/connection handling #
    #############################

    configpath = ['/etc/bugzillarc', '~/.bugzillarc']

    def readconfig(self, configpath=None):
        '''
        Read bugzillarc file(s) into memory.
        '''
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
        log.debug("Searching for config section matching %s", self.url)
        for s in sorted(c.sections(),
                        lambda a, b: cmp(len(a), len(b)) or cmp(a, b)):
            if s in self.url:
                log.debug("Found matching section: %s" % s)
                section = s
        if not section:
            return
        for k, v in c.items(section):
            if k in ('user', 'password'):
                log.debug("Setting '%s' from configfile" % k)
                setattr(self, k, v)

    def connect(self, url):
        '''
        Connect to the bugzilla instance with the given url.

        This will also read any available config files (see readconfig()),
        which may set 'user' and 'password'.

        If 'user' and 'password' are both set, we'll run login(). Otherwise
        you'll have to login() yourself before some methods will work.
        '''
        if not '://' in url:
            log.debug('No scheme given for url, assuming https')
            url = 'https://' + url
        if url.count('/') < 3:
            log.debug('No path given for url, assuming /xmlrpc.cgi')
            url = url + '/xmlrpc.cgi'
        # Set up the transport
        if url.startswith('https'):
            self._transport = SafeCookieTransport()
        else:
            self._transport = CookieTransport()
        self._transport.user_agent = self.user_agent
        self._transport.cookiejar = self._cookiejar
        # Set up the proxy, using the transport
        self._proxy = xmlrpclib.ServerProxy(url, self._transport)
        # Set up the urllib2 opener (using the same cookiejar)
        handler = urllib2.HTTPCookieProcessor(self._cookiejar)
        self._opener = urllib2.build_opener(handler)
        self._opener.addheaders = [('User-agent', self.user_agent)]
        self.url = url

        # we've changed URLs - reload config
        self.readconfig()

        if (self.user and self.password):
            log.info("user and password present - doing login()")
            self.login()

    def disconnect(self):
        '''
        Disconnect from the given bugzilla instance.
        '''
        # clears all the connection state
        self._init_private_data()

    def login(self, user=None, password=None):
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
            raise ValueError("missing username")
        if not self.password:
            raise ValueError("missing password")

        try:
            r = self._login(self.user, self.password)
            self.logged_in = True
            log.info("login successful - dropping password from memory")
            self.password = ''
        except xmlrpclib.Fault:
            r = False
        return r

    def logout(self):
        '''Log out of bugzilla. Drops server connection and user info, and
        destroys authentication cookies.'''
        self._logout()
        self.disconnect()
        self.user = ''
        self.password = ''
        self.logged_in = False


    #############################################
    # Fetching info about the bugzilla instance #
    #############################################

    def getbugfields(self, force_refresh=False):
        '''
        Calls getBugFields, which returns a list of fields in each bug
        for this bugzilla instance. This can be used to set the list of attrs
        on the Bug object.
        '''
        if force_refresh or self._bugfields is None:
            log.debug("Refreshing bugfields")
            try:
                self._bugfields = self._getbugfields()
            except xmlrpclib.Fault, f:
                if f.faultCode == 'Client':
                    # okay, this instance doesn't have getbugfields. fine.
                    self._bugfields = []
                else:
                    # something bad actually happened on the server. blow up.
                    raise f
            self._bugfields.sort()
            log.debug("bugfields = %s", self._bugfields)

        return self._bugfields
    bugfields = property(fget=lambda self: self.getbugfields(),
                         fdel=lambda self: setattr(self, '_bugfields', None))

    def getqueryinfo(self, force_refresh=False):
        '''
        Calls getQueryInfo, which returns a (quite large!) structure that
        contains all of the query data and query defaults for the bugzilla
        instance. Since this is a weighty call - takes a good 5-10sec on
        bugzilla.redhat.com - we load the info in this private method and the
        user instead plays with the querydata and querydefaults attributes of
        the bugzilla object.
        '''
        if force_refresh or not (self._querydata and self._querydefaults):
            (self._querydata, self._querydefaults) = self._getqueryinfo()
        return (self._querydata, self._querydefaults)

    # Set querydata and querydefaults as properties so they auto-create
    # themselves when touched by a user. This bit was lifted from YumBase.
    querydata = property(fget=lambda self: self.getqueryinfo()[0],
                         fdel=lambda self: setattr(self, "_querydata", None))
    querydefaults = property(fget=lambda self: self.getqueryinfo()[1],
                     fdel=lambda self: setattr(self, "_querydefaults", None))


    def refresh_products(self, **kwargs):
        """
        Refresh a product's cached info
        Takes same arguments as _getproductinfo
        """
        for product in self._getproductinfo(**kwargs):
            for current in self.products[:]:
                if (current.get("id", -1) != product.get("id", -2) and
                    current.get("name", -1) != product.get("name", -2)):
                    continue

                self.products.remove(current)
                self.products.append(product)
                break

    def getproducts(self, force_refresh=False, **kwargs):
        '''Get product data: names, descriptions, etc.
        The data varies between Bugzilla versions but the basic format is a
        list of dicts, where the dicts will have at least the following keys:
        {'id':1, 'name':"Some Product", 'description':"This is a product"}

        Any method that requires a 'product' can be given either the
        id or the name.'''
        if force_refresh or not self._products:
            self._products = self._getproducts(**kwargs)
        return self._products

    products = property(fget=lambda self: self.getproducts(),
                        fdel=lambda self: setattr(self, '_products', None))


    def getcomponentsdetails(self, product, force_refresh=False):
        '''Returns a dict of dicts, containing detailed component information
        for the given product. The keys of the dict are component names. For
        each component, the value is a dict with the following keys:
        description, initialowner, initialqacontact'''
        if force_refresh or product not in self._components_details:
            clist = self._getcomponentsdetails(product)
            cdict = {}
            for item in clist:
                name = item['component']
                del item['component']
                cdict[name] = item
            self._components_details[product] = cdict

        return self._components_details[product]

    def getcomponentdetails(self, product, component, force_refresh=False):
        '''Get details for a single component. Returns a dict with the
        following keys:
        description, initialowner, initialqacontact, initialcclist'''
        d = self.getcomponentsdetails(product, force_refresh)
        return d[component]

    def getcomponents(self, product, force_refresh=False):
        '''Return a dict of components:descriptions for the given product.'''
        if force_refresh or product not in self._components:
            self._components[product] = self._getcomponents(product)
        return self._components[product]

    def addcomponent(self, data):
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

    def editcomponent(self, data):
        '''A method to edit a component in Bugzilla. Takes a dict, with
            mandatory elements of product. component, and initialowner.
            All other elements are optional and use the same names as the
            addcomponent() method.'''
        self._editcomponent(data)


    def _getproductinfo(self, ids=None, names=None,
                        include_fields=None, exclude_fields=None):
        '''
        Get all info for the requested products.

        @ids: List of product IDs to lookup
        @names: List of product names to lookup (since bz 4.2,
            though we emulate it for older versions)
        @include_fields: Only include these fields in the output (since bz 4.2)
        @exclude_fields: Do not include these fields in the output (since
            bz 4.2)
        '''
        if ids is None and names is None:
            raise RuntimeError("Products must be specified")

        kwargs = {}
        if not self._check_version(4, 2):
            if names:
                ids = [self._product_name_to_id(name) for name in names]
                names = None
            include_fields = None
            exclude_fields = None

        if ids:
            kwargs["ids"] = self._listify(ids)
        if names:
            kwargs["names"] = self._listify(names)
        if include_fields:
            kwargs["include_fields"] = include_fields
        if exclude_fields:
            kwargs["exclude_fields"] = exclude_fields

        # The bugzilla4 name is Product.get(), but Bugzilla3 only had
        # Product.get_product, and bz4 kept an alias.
        ret = self._proxy.Product.get_products(kwargs)
        return ret['products']

    def _getproducts(self, **kwargs):
        product_ids = self._proxy.Product.get_accessible_products()
        r = self._getproductinfo(product_ids['ids'], **kwargs)
        return r

    def _getcomponentsdetails(self, product):
        # Originally this was a RH extension getProdCompDetails
        # Upstream support has been available since 4.2
        if not self._check_version(4, 2):
            raise RuntimeError("This bugzilla version does not support "
                               "fetching component details.")

        comps = None
        for p in self.products:
            if p["name"] != product:
                continue
            comps = p["components"]

        if not comps:
            raise ValueError("Unknown product '%s'" % product)

        # Convert to old style dictionary to maintain back compat
        # with original RH bugzilla call
        ret = []
        for comp in comps:
            row = {}
            row["component"] = comp["name"]
            row["initialqacontact"] = comp["default_qa_contact"]
            row["initialowner"] = comp["default_assigned_to"]
            row["description"] = comp["description"]
            ret.append(row)
        return ret


    ###################
    # getbug* methods #
    ###################

    # getbug_extra_fields: Extra fields that need to be explicitly
    # requested from Bug.get in order for the data to be returned. This
    # decides the difference between getbug() and getbugsimple().
    #
    # As of Dec 2012 it seems like only RH bugzilla actually has behavior
    # like this, for upstream bz it returns all info for every Bug.get()
    getbug_extra_fields = []

    # List of field aliases. Maps old style RHBZ parameter names to actual
    # upstream values. Used for createbug() and query include_fields at
    # least.
    #
    # Format is (currentname, oldname)
    field_aliases = (
        ('summary', 'short_desc'),
        ('description', 'comment'),
        ('platform', 'rep_platform'),
        ('severity', 'bug_severity'),
        ('status', 'bug_status'),
        ('id', 'bug_id'),
        ('blocks', 'blockedby'),
        ('blocks', 'blocked'),
        ('depends_on', 'dependson'),
        ('creator', 'reporter'),
        ('url', 'bug_file_loc'),
        ('dupe_of', 'dupe_id'),
        ('dupe_of', 'dup_id'),
        ('comments', 'longdescs'),
        ('creation_time', 'opendate'),
        ('creation_time', 'creation_ts'),
        ('whiteboard', 'status_whiteboard'),
    )


    def getbug(self, objid,):
        '''Return a Bug object with the full complement of bug data
        already loaded.'''
        log.debug("getbug(%s)" % str(objid))
        return _Bug(bugzilla=self, dict=self._getbug(objid))

    def getbugsimple(self, objid):
        '''Return a Bug object given bug id, populated with simple info'''
        return _Bug(bugzilla=self, dict=self._getbugsimple(objid))

    def getbugs(self, idlist):
        '''Return a list of Bug objects with the full complement of bug data
        already loaded. If there's a problem getting the data for a given id,
        the corresponding item in the returned list will be None.'''
        return [(b and _Bug(bugzilla=self, dict=b)) or None
                for b in self._getbugs(idlist)]

    def getbugssimple(self, idlist):
        '''Return a list of Bug objects for the given bug ids, populated with
        simple info. As with getbugs(), if there's a problem getting the data
        for a given bug ID, the corresponding item in the returned list will
        be None.'''
        return [(b and _Bug(bugzilla=self, dict=b)) or None
                for b in self._getbugssimple(idlist)]


    #################
    # query methods #
    #################

    def build_query(self, *args, **kwargs):
        raise NotImplementedError("This version of bugzilla does not "
                                  "support bug querying.")

    def query(self, query):
        '''Query bugzilla and return a list of matching bugs.
        query must be a dict with fields like those in in querydata['fields'].
        Returns a list of Bug objects.
        Also see the _query() method for details about the underlying
        implementation.
        '''
        log.debug("Calling query with: %s", query)
        r = self._query(query)
        log.debug("Query returned %s bugs", len(r['bugs']))
        return [_Bug(bugzilla=self, dict=b) for b in r['bugs']]

    def simplequery(self, product, version='', component='',
                    string='', matchtype='allwordssubstr'):
        '''Convenience method - query for bugs filed against the given
        product, version, and component whose comments match the given string.
        matchtype specifies the type of match to be done. matchtype may be
        any of the types listed in querydefaults['long_desc_type_list'], e.g.:
        ['allwordssubstr', 'anywordssubstr', 'substring', 'casesubstring',
         'allwords', 'anywords', 'regexp', 'notregexp']
        Return value is the same as with query().
        '''
        q = {
            'product': product,
            'version': version,
            'component': component,
            'long_desc': string,
            'long_desc_type': matchtype
        }
        return self.query(q)

    def pre_translation(self, query):
        '''In order to keep the API the same, Bugzilla4 needs to process the
        query and the result. This also applies to the refresh() function
        '''
        pass

    def post_translation(self, query, bug):
        '''In order to keep the API the same, Bugzilla4 needs to process the
        query and the result. This also applies to the refresh() function
        '''
        pass


    #######################################
    # Methods for modifying existing bugs #
    #######################################

    # Bug() also has individual methods for many ops, like setassignee()

    def update_bugs(self, ids, updates):
        """
        A thin wrapper around bugzilla Bug.update(). Used to update all
        values of an existing bug report, as well as add comments.

        The dictionary passed to this function should be generated with
        build_update(), otherwise we cannot guarantee back compatibility.
        """
        tmp = updates.copy()
        tmp["ids"] = self._listify(ids)

        return self._proxy.Bug.update(tmp)

    def build_update(self, *args, **kwargs):
        raise NotImplementedError("This bugzilla instance does not support "
                "modifying bugs")


    ########################################
    # Methods for working with attachments #
    ########################################

    def attachfile(self, idlist, attachfile, description, **kwargs):
        '''
        Attach a file to the given bug IDs. Returns the ID of the attachment
        or raises xmlrpclib.Fault if something goes wrong.
        attachfile may be a filename (which will be opened) or a file-like
        object, which must provide a 'read' method. If it's not one of these,
        this method will raise a TypeError.
        description is the short description of this attachment.
        Optional keyword args are as follows:
            file_name:  this will be used as the filename for the attachment.
                       REQUIRED if attachfile is a file-like object with no
                       'name' attribute, otherwise the filename or .name
                       attribute will be used.
            comment:   An optional comment about this attachment.
            is_private: Set to True if the attachment should be marked private.
            is_patch:   Set to True if the attachment is a patch.
            content_type: The mime-type of the attached file. Defaults to
                         application/octet-stream if not set. NOTE that text
                         files will *not* be viewable in bugzilla unless you
                         remember to set this to text/plain. So remember that!

        Returns the list of attachment ids that were added. If only one
        attachment was added, we return the single int ID for back compat
        '''
        if isinstance(attachfile, str):
            f = open(attachfile)
        elif hasattr(attachfile, 'read'):
            f = attachfile
        else:
            raise TypeError("attachfile must be filename or file-like object")

        # Back compat
        if "contenttype" in kwargs:
            kwargs["content_type"] = kwargs.pop("contenttype")
        if "ispatch" in kwargs:
            kwargs["is_patch"] = kwargs.pop("ispatch")
        if "isprivate" in kwargs:
            kwargs["is_private"] = kwargs.pop("isprivate")
        if "filename" in kwargs:
            kwargs["file_name"] = kwargs.pop("filename")

        kwargs['summary'] = description
        if 'file_name' not in kwargs:
            kwargs['file_name'] = os.path.basename(f.name)

        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'application/octet-stream'

        kwargs['data'] = self._attachment_encode(f)
        kwargs['ids'] = self._listify(idlist)

        ret = self._proxy.Bug.add_attachment(kwargs)

        if "attachments" in ret:
            # Up to BZ 4.2
            ret = [int(k) for k in ret["attachments"].keys()]
        elif "ids" in ret:
            # BZ 4.4+
            ret = ret["ids"]

        if type(ret) is list and len(ret) == 1:
            ret = ret[0]
        return ret


    def openattachment(self, attachid):
        '''Get the contents of the attachment with the given attachment ID.
        Returns a file-like object.'''
        att_uri = self._attachment_uri(attachid)
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookiejar))
        att = opener.open(att_uri)

        # RFC 2183 defines the content-disposition header, if you're curious
        disp = att.headers['content-disposition'].split(';')
        disp.pop(0)
        parms = dict([p.strip().split("=", 1) for p in disp])
        # Parameter values can be quoted/encoded as per RFC 2231
        att.name = _decode_rfc2231_value(parms['filename'])
        # Hooray, now we have a file-like object with .read() and .name
        return att

    def _attachment_uri(self, attachid):
        '''Returns the URI for the given attachment ID.'''
        att_uri = self.url.replace('xmlrpc.cgi', 'attachment.cgi')
        att_uri = att_uri + '?id=%s' % attachid
        return att_uri

    def _attachment_encode(self, fh):
        '''Return the contents of the file-like object fh in a form
        appropriate for attaching to a bug in bugzilla. This is the default
        encoding method, base64.'''
        # Read data in chunks so we don't end up with two copies of the file
        # in RAM.

        # base64 encoding wants input in multiples of 3
        chunksize = 3072
        data = ''
        chunk = fh.read(chunksize)
        while chunk:
            # we could use chunk.encode('base64') but that throws a newline
            # at the end of every output chunk, which increases the size of
            # the output.
            data = data + base64.b64encode(chunk)
            chunk = fh.read(chunksize)
        return data


    #####################
    # createbug methods #
    #####################

    createbug_required = ('product', 'component', 'summary', 'version',
                          'description')

    def createbug(self, **data):
        '''
        Create a bug with the given info. Returns a new Bug object.
        Check bugzilla API documentation for valid values, at least
        product, component, summary, version, and description need to
        be passed.
        '''
        log.debug("bz.createbug(%s)", data)

        # If we're getting a call that uses an old fieldname, convert it to the
        # new fieldname instead.
        for newfield, oldfield in self.field_aliases:
            if (newfield in self.createbug_required and
                newfield not in data and
                oldfield in data):
                data[newfield] = data.pop(oldfield)

        # Back compat handling for check_args
        if "check_args" in data:
            del(data["check_args"])

        bug_id = self._createbug(**data)
        return _Bug(self, bug_id=bug_id)


    ##############################
    # Methods for handling Users #
    ##############################

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
            real_name=rawuser.get('real_name', ''),
            email=rawuser.get('email', rawuser['name']),
            can_login=rawuser.get('can_login', False))
            for rawuser in self._getusers(names=userlist)['users']]

    def searchusers(self, pattern):
        '''Return a bugzilla User for the given list of patterns

        :arg pattern: List of patterns to match against.
        :returns: List of User records
        '''
        return [_User(self, userid=rawuser['id'], name=rawuser['name'],
            real_name=rawuser.get('real_name', ''),
            email=rawuser.get('email', rawuser['name']),
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
        self._createuser(email, name, password)
        return self.getuser(email)


    ######################################################
    # Internal API methods, overwritten by child classes #
    ######################################################

    def _login(self, user, password):
        '''IMPLEMENT ME: backend login method'''
        raise NotImplementedError

    def _logout(self):
        '''IMPLEMENT ME: backend login method'''
        raise NotImplementedError

    def _getbugfields(self):
        '''IMPLEMENT ME: Get bugfields from Bugzilla.'''
        raise NotImplementedError

    def _getqueryinfo(self):
        '''IMPLEMENT ME: Get queryinfo from Bugzilla.'''
        raise NotImplementedError

    def _getcomponents(self, product):
        '''IMPLEMENT ME: Get component dict for a product'''
        raise NotImplementedError

    def _addcomponent(self, data):
        '''IMPLEMENT ME: Add a component'''
        raise NotImplementedError

    def _editcomponent(self, data):
        '''IMPLEMENT ME: Edit a component'''
        raise NotImplementedError


    def _getbug(self, objid):
        '''IMPLEMENT ME: Return a dict of full bug info for the given bug id'''
        raise NotImplementedError

    def _getbugs(self, idlist):
        '''IMPLEMENT ME: Return a list of full bug dicts, one for each of the
        given bug ids'''
        raise NotImplementedError

    def _getbugsimple(self, objid):
        '''IMPLEMENT ME: Return a short dict of simple bug info for the given
        bug id'''
        raise NotImplementedError

    def _getbugssimple(self, idlist):
        '''IMPLEMENT ME: Return a list of short bug dicts, one for each of the
        given bug ids'''
        raise NotImplementedError



    def _getusers(self, ids=None, names=None, match=None):
        '''IMPLEMEMT ME: Get a list of Bugzilla user'''
        raise NotImplementedError

    def _createuser(self, email, name=None, password=None):
        '''IMPLEMEMT ME: Create a Bugzilla user'''
        raise NotImplementedError

    def _updateperms(self, user, action, group):
        '''IMPLEMEMT ME: Update Bugzilla user permissions'''
        raise NotImplementedError

    def _adduser(self, email, name):
        '''IMPLEMENT ME: Add a bugzilla user

        Deprecated.  User _createuser() instead
        '''
        raise NotImplementedError


    def _createbug(self, **data):
        '''IMPLEMENT ME: Raw xmlrpc call for createBug()
        Doesn't bother guessing defaults or checking argument validity.
        Returns bug_id'''
        raise NotImplementedError

    def _query(self, query):
        '''IMPLEMENT ME: Query bugzilla and return a list of matching bugs.'''
        raise NotImplementedError("This version of bugzilla does not "
                                  "support bug querying.")


    ######################
    # Deprecated methods #
    ######################

    def initcookiefile(self, cookiefile=None):
        '''
        Deprecated: Set self.cookiefile instead.
        '''
        if not cookiefile:
            cookiefile = os.path.expanduser('~/.bugzillacookies')
        self.cookiefile = cookiefile

    def updateperms(self, user, action, groups):
        '''A method to update the permissions (group membership) of a bugzilla
        user.  Deprecated.  Use User.updateperms(action, group) instead.

        :arg user: The e-mail address of the user to be acted upon
        :arg action: either add or rem
        :arg groups: list of groups to be added to (i.e. ['fedora_contrib'])
        '''
        self._updateperms(user, action, groups)

    def adduser(self, user, name):
        '''Deprecated: Use createuser() instead.

        A method to create a user in Bugzilla. Takes the following:

        user: The email address of the user to create
        name: The full name of the user to create
        '''
        self._adduser(user, name)
