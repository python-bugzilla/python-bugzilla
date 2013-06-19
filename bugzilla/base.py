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
import os
import StringIO
import urllib2
import urlparse
import xmlrpclib

import pycurl

from bugzilla import __version__, log
from bugzilla.bug import _Bug, _User


# Backwards compatibility
Bug = _Bug

mimemagic = None


def _detect_filetype(fname):
    global mimemagic

    if mimemagic is None:
        try:
            import magic
            mimemagic = magic.open(magic.MAGIC_MIME_TYPE)
            mimemagic.load()
        except ImportError, e:
            log.debug("Could not load python-magic: %s", e)
            mimemagic = False
    if mimemagic is False:
        return None

    if not os.path.isabs(fname):
        return None

    try:
        return mimemagic.file(fname)
    except Exception, e:
        log.debug("Could not detect content_type: %s", e)
    return None


def _decode_rfc2231_value(val):
    # BUG WORKAROUND: decode_header doesn't work unless there's whitespace
    # around the encoded string (see http://bugs.python.org/issue1079)
    from email import utils
    from email import header

    # pylint: disable=W1401
    # Anomolous backslash in string
    val = utils.ecre.sub(' \g<0> ', val)
    val = val.strip('"')
    return ''.join(f[0].decode(f[1] or 'us-ascii')
                   for f in header.decode_header(val))


def _build_cookiejar(cookiefile):
    cj = cookielib.MozillaCookieJar(cookiefile)
    if cookiefile is None:
        return cj
    if not os.path.exists(cookiefile):
        # Make sure a new file has correct permissions
        open(cookiefile, 'a').close()
        os.chmod(cookiefile, 0600)
        cj.save()
        return cj

    # We always want to use Mozilla cookies, but we previously accepted
    # LWP cookies. If we see the latter, convert it to former
    try:
        cj.load()
        return cj
    except cookielib.LoadError:
        pass

    try:
        cj = cookielib.LWPCookieJar(cookiefile)
        cj.load()
    except cookielib.LoadError:
        raise BugzillaError("cookiefile=%s not in LWP or Mozilla format" %
                            cookiefile)

    retcj = cookielib.MozillaCookieJar(cookiefile)
    for cookie in cj:
        retcj.set_cookie(cookie)
    retcj.save()
    return retcj


class _CURLTransport(xmlrpclib.Transport):
    def __init__(self, url, cookiejar,
                 sslverify=True, sslcafile=None, debug=0):
        if hasattr(xmlrpclib.Transport, "__init__"):
            xmlrpclib.Transport.__init__(self, use_datetime=False)

        self.verbose = debug

        # transport constructor needs full url too, as xmlrpc does not pass
        # scheme to request
        self.scheme = urlparse.urlparse(url)[0]
        if self.scheme not in ["http", "https"]:
            raise Exception("Invalid URL scheme: %s (%s)" % (self.scheme, url))

        self.c = pycurl.Curl()
        self.c.setopt(pycurl.POST, 1)
        self.c.setopt(pycurl.CONNECTTIMEOUT, 30)
        self.c.setopt(pycurl.HTTPHEADER, [
            "Content-Type: text/xml",
        ])
        self.c.setopt(pycurl.VERBOSE, debug)

        self.set_cookiejar(cookiejar)

        # ssl settings
        if self.scheme == "https":
            # override curl built-in ca file setting
            if sslcafile is not None:
                self.c.setopt(pycurl.CAINFO, sslcafile)

            # disable ssl verification
            if not sslverify:
                self.c.setopt(pycurl.SSL_VERIFYPEER, 0)
                self.c.setopt(pycurl.SSL_VERIFYHOST, 0)

    def set_cookiejar(self, cj):
        self.c.setopt(pycurl.COOKIEFILE, cj.filename or "")
        self.c.setopt(pycurl.COOKIEJAR, cj.filename or "")

    def get_cookies(self):
        return self.c.getinfo(pycurl.INFO_COOKIELIST)

    def open_helper(self, url, request_body):
        self.c.setopt(pycurl.URL, url)
        self.c.setopt(pycurl.POSTFIELDS, request_body)

        b = StringIO.StringIO()
        self.c.setopt(pycurl.WRITEFUNCTION, b.write)
        try:
            self.c.perform()
        except pycurl.error, e:
            raise xmlrpclib.ProtocolError(url, e[0], e[1], None)

        b.seek(0)
        return b

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        url = "%s://%s%s" % (self.scheme, host, handler)

        # xmlrpclib fails to escape \r
        request_body = request_body.replace('\r', '&#xd;')

        stringio = self.open_helper(url, request_body)
        return self.parse_response(stringio)




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
        q = {}
        (ignore, ignore, path,
         ignore, query, ignore) = urlparse.urlparse(url)

        if os.path.basename(path) not in ('buglist.cgi', 'query.cgi'):
            return {}

        for (k, v) in urlparse.parse_qsl(query):
            if k not in q:
                q[k] = v
            elif isinstance(q[k], list):
                q[k].append(v)
            else:
                oldv = q[k]
                q[k] = [oldv, v]

        return q

    @staticmethod
    def fix_url(url):
        """
        Turn passed url into a bugzilla XMLRPC web url
        """
        if not '://' in url:
            log.debug('No scheme given for url, assuming https')
            url = 'https://' + url
        if url.count('/') < 3:
            log.debug('No path given for url, assuming /xmlrpc.cgi')
            url = url + '/xmlrpc.cgi'
        return url

    def __init__(self, url=None, user=None, password=None, cookiefile=-1,
                 sslverify=True):
        # Settings the user might want to tweak
        self.user = user or ''
        self.password = password or ''
        self.url = ''

        self._transport = None
        self._cookiejar = None
        self._sslverify = bool(sslverify)

        self.logged_in = False

        # Bugzilla object state info that users shouldn't mess with
        self._proxy = None
        self._products = None
        self._bugfields = None
        self._components = {}
        self._components_details = {}
        self._init_private_data()

        if cookiefile == -1:
            cookiefile = os.path.expanduser('~/.bugzillacookies')
        self.cookiefile = cookiefile

        if url:
            self.connect(url)

    def _init_private_data(self):
        '''initialize private variables used by this bugzilla instance.'''
        self._proxy = None
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
        return self._cookiejar.filename

    def _delcookiefile(self):
        self._cookiejar = None

    def _setcookiefile(self, cookiefile):
        if (self._cookiejar and cookiefile == self._cookiejar.filename):
            return

        if self._proxy is not None:
            raise RuntimeError("Can't set cookies with an open connection, "
                               "disconnect() first.")

        log.debug("Using cookiefile=%s", cookiefile)
        self._cookiejar = _build_cookiejar(cookiefile)

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

    def connect(self, url=None):
        '''
        Connect to the bugzilla instance with the given url.

        This will also read any available config files (see readconfig()),
        which may set 'user' and 'password'.

        If 'user' and 'password' are both set, we'll run login(). Otherwise
        you'll have to login() yourself before some methods will work.
        '''
        if url is None and self.url:
            url = self.url
        url = self.fix_url(url)

        self._transport = _CURLTransport(url, self._cookiejar,
                                         sslverify=self._sslverify)
        self._transport.user_agent = self.user_agent
        self._proxy = xmlrpclib.ServerProxy(url, self._transport)


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


    def _login(self, user, password):
        '''Backend login method for Bugzilla3'''
        return self._proxy.User.login({'login': user, 'password': password})

    def _logout(self):
        '''Backend login method for Bugzilla3'''
        return self._proxy.User.logout()

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

    def _getbugfields(self):
        '''IMPLEMENT ME: Get bugfields from Bugzilla.'''
        raise NotImplementedError

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

    def _component_data_convert(self, data, update=False):
        if type(data['product']) is int:
            data['product'] = self._product_id_to_name(data['product'])


        # Back compat for the old RH interface
        convert_fields = [
            ("initialowner", "default_assignee"),
            ("initialqacontact", "default_qa_contact"),
            ("initialcclist", "default_cc"),
        ]
        for old, new in convert_fields:
            if old in data:
                data[new] = data.pop(old)

        if update:
            names = {"product": data.pop("product"),
                     "component": data.pop("component")}
            updates = {}
            for k in data.keys():
                updates[k] = data.pop(k)

            data["names"] = [names]
            data["updates"] = updates


    def addcomponent(self, data):
        '''
        A method to create a component in Bugzilla. Takes a dict, with the
        following elements:

        product: The product to create the component in
        component: The name of the component to create
        desription: A one sentence summary of the component
        default_assignee: The bugzilla login (email address) of the initial
                          owner of the component
        default_qa_contact (optional): The bugzilla login of the
                                       initial QA contact
        default_cc: (optional) The initial list of users to be CC'ed on
                               new bugs for the component.
        '''
        data = data.copy()
        self._component_data_convert(data)
        return self._proxy.Component.create(data)

    def editcomponent(self, data):
        '''
        A method to edit a component in Bugzilla. Takes a dict, with
        mandatory elements of product. component, and initialowner.
        All other elements are optional and use the same names as the
        addcomponent() method.
        '''
        data = data.copy()
        self._component_data_convert(data, update=True)
        return self._proxy.Component.update(data)


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

    def _getcomponents(self, product):
        if type(product) == str:
            product = self._product_name_to_id(product)
        r = self._proxy.Bug.legal_values({'product_id': product,
                                          'field': 'component'})
        return r['values']

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
        ('last_change_time', 'delta_ts'),
    )

    def _getbugs(self, idlist, simple=False, permissive=True):
        '''
        Return a list of dicts of full bug info for each given bug id.
        bug ids that couldn't be found will return None instead of a dict.

        @simple: If True, don't ask for any large extra_fields.
        '''
        idlist = [int(i) for i in idlist]

        getbugdata = {"ids": idlist}
        if permissive:
            getbugdata["permissive"] = 1
        if self.getbug_extra_fields and not simple:
            getbugdata["extra_fields"] = self.getbug_extra_fields

        r = self._proxy.Bug.get_bugs(getbugdata)

        if self.bz_ver_major >= 4:
            bugdict = dict([(b['id'], b) for b in r['bugs']])
        else:
            bugdict = dict([(b['id'], b['internals']) for b in r['bugs']])

        return [bugdict.get(i) for i in idlist]

    def _getbug(self, objid, simple=False):
        '''Return a dict of full bug info for the given bug id'''
        return self._getbugs([objid], simple=simple, permissive=False)[0]

    def getbug(self, objid):
        '''Return a Bug object with the full complement of bug data
        already loaded.'''
        log.debug("getbug(%s)" % str(objid))
        return _Bug(bugzilla=self, dict=self._getbug(objid))

    def getbugs(self, idlist):
        '''Return a list of Bug objects with the full complement of bug data
        already loaded. If there's a problem getting the data for a given id,
        the corresponding item in the returned list will be None.'''
        return [(b and _Bug(bugzilla=self, dict=b)) or None
                for b in self._getbugs(idlist)]

    # Since for so long getbugsimple was just getbug, I don't think we can
    # remove any fields without possibly causing a slowdown for some
    # existing users. Just have this API mean 'don't ask for the extra
    # big stuff'
    def getbugsimple(self, objid):
        '''Return a Bug object given bug id, populated with simple info'''
        return _Bug(bugzilla=self, dict=self._getbug(objid, simple=True))

    def getbugssimple(self, idlist):
        '''Return a list of Bug objects for the given bug ids, populated with
        simple info. As with getbugs(), if there's a problem getting the data
        for a given bug ID, the corresponding item in the returned list will
        be None.'''
        return [(b and _Bug(bugzilla=self, dict=b)) or None
                for b in self._getbugs(idlist, simple=True)]


    #################
    # query methods #
    #################


    def build_query(self,
                    product=None,
                    component=None,
                    version=None,
                    long_desc=None,
                    bug_id=None,
                    short_desc=None,
                    cc=None,
                    assigned_to=None,
                    reporter=None,
                    qa_contact=None,
                    status=None,
                    blocked=None,
                    dependson=None,
                    keywords=None,
                    keywords_type=None,
                    url=None,
                    url_type=None,
                    status_whiteboard=None,
                    status_whiteboard_type=None,
                    fixed_in=None,
                    fixed_in_type=None,
                    flag=None,
                    alias=None,
                    qa_whiteboard=None,
                    devel_whiteboard=None,
                    boolean_query=None,
                    bug_severity=None,
                    priority=None,
                    target_milestone=None,
                    emailtype=None,
                    booleantype=None,
                    include_fields=None):
        """
        Build a query string from passed arguments. Will handle
        query parameter differences between various bugzilla versions.

        Most of the parameters should be self explanatory. However
        if you want to perform a complex query, and easy way is to
        create it with the bugzilla web UI, copy the entire URL it
        generates, and pass it to the static method

        Bugzilla.url_to_query

        Then pass the output to Bugzilla.query()
        """
        # pylint: disable=W0221
        # Argument number differs from overridden method
        # Base defines it with *args, **kwargs, so we don't have to maintain
        # the master argument list in 2 places

        ignore = include_fields
        ignore = emailtype
        ignore = booleantype

        for key, val in [
            ('fixed_in', fixed_in),
            ('blocked', blocked),
            ('dependson', dependson),
            ('flag', flag),
            ('qa_whiteboard', qa_whiteboard),
            ('devel_whiteboard', devel_whiteboard),
            ('alias', alias),
            ('boolean_query', boolean_query),
        ]:
            if not val is None:
                raise RuntimeError("'%s' search not supported by this "
                                   "bugzilla" % key)

        query = {
            "product": self._listify(product),
            "component": self._listify(component),
            "version": version,
            "long_desc": long_desc,
            "id": bug_id,
            "short_desc": short_desc,
            "bug_status": status,
            "keywords": keywords,
            "keywords_type": keywords_type,
            "bug_file_loc": url,
            "bug_file_loc_type": url_type,
            "status_whiteboard": status_whiteboard,
            "status_whiteboard_type": status_whiteboard_type,
            "fixed_in_type": fixed_in_type,
            "bug_severity": bug_severity,
            "priority": priority,
            "target_milestone": target_milestone,
            "assigned_to": assigned_to,
            "cc": cc,
            "qa_contact": qa_contact,
            "reporter": reporter,
        }

        # Strip out None elements in the dict
        for key in query.keys():
            if query[key] is None:
                del(query[key])
        return query

    def _query(self, query):
        # This is kinda redundant now, but various scripts call
        # _query with their own assembled dictionaries, so don't
        # drop this lest we needlessly break those users
        return self._proxy.Bug.search(query)

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

    def bugs_history(self, bug_ids):
        '''
        Experimental. Gets the history of changes for
        particular bugs in the database.
        '''
        return self._proxy.Bug.history({'ids': bug_ids})

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

    def update_flags(self, idlist, flags):
        '''
        Updates the flags associated with a bug report.
        Format of flags is:
        [{"name": "needinfo", "status": "+", "requestee": "foo@bar.com"},
         {"name": "devel_ack", "status": "-"}, ...]
        '''
        d = {"ids": self._listify(idlist), "updates": flags}
        return self._proxy.Flag.update(d)


    def build_update(self,
                     alias=None,
                     assigned_to=None,
                     blocks_add=None,
                     blocks_remove=None,
                     blocks_set=None,
                     depends_on_add=None,
                     depends_on_remove=None,
                     depends_on_set=None,
                     cc_add=None,
                     cc_remove=None,
                     is_cc_accessible=None,
                     comment=None,
                     comment_private=None,
                     component=None,
                     deadline=None,
                     dupe_of=None,
                     estimated_time=None,
                     groups_add=None,
                     groups_remove=None,
                     keywords_add=None,
                     keywords_remove=None,
                     keywords_set=None,
                     op_sys=None,
                     platform=None,
                     priority=None,
                     product=None,
                     qa_contact=None,
                     is_creator_accessible=None,
                     remaining_time=None,
                     reset_assigned_to=None,
                     reset_qa_contact=None,
                     resolution=None,
                     see_also_add=None,
                     see_also_remove=None,
                     severity=None,
                     status=None,
                     summary=None,
                     target_milestone=None,
                     target_release=None,
                     url=None,
                     version=None,
                     whiteboard=None,
                     work_time=None,
                     fixed_in=None,
                     qa_whiteboard=None,
                     devel_whiteboard=None,
                     internal_whiteboard=None):
        # pylint: disable=W0221
        # Argument number differs from overridden method
        # Base defines it with *args, **kwargs, so we don't have to maintain
        # the master argument list in 2 places
        ret = {}

        # These are only supported for rhbugzilla
        for key, val in [
            ("fixed_in", fixed_in),
            ("devel_whiteboard", devel_whiteboard),
            ("qa_whiteboard", qa_whiteboard),
            ("internal_whiteboard", internal_whiteboard),
        ]:
            if val is not None:
                raise ValueError("bugzilla instance does not support "
                                 "updating '%s'" % key)

        def s(key, val, convert=None):
            if val is None:
                return
            if convert:
                val = convert(val)
            ret[key] = val

        def add_dict(key, add, remove, _set=None, convert=None):
            if add is remove is _set is None:
                return

            def c(val):
                val = self._listify(val)
                if convert:
                    val = [convert(v) for v in val]
                return val

            newdict = {}
            if add is not None:
                newdict["add"] = c(add)
            if remove is not None:
                newdict["remove"] = c(remove)
            if _set is not None:
                newdict["set"] = c(_set)
            ret[key] = newdict


        s("alias", alias)
        s("assigned_to", assigned_to)
        s("is_cc_accessible", is_cc_accessible, bool)
        s("component", component)
        s("deadline", deadline)
        s("dupe_of", dupe_of, int)
        s("estimated_time", estimated_time, int)
        s("op_sys", op_sys)
        s("platform", platform)
        s("priority", priority)
        s("product", product)
        s("qa_contact", qa_contact)
        s("is_creator_accessible", is_creator_accessible, bool)
        s("remaining_time", remaining_time, float)
        s("reset_assigned_to", reset_assigned_to, bool)
        s("reset_qa_contact", reset_qa_contact, bool)
        s("resolution", resolution)
        s("severity", severity)
        s("status", status)
        s("summary", summary)
        s("target_milestone", target_milestone)
        s("target_release", target_release)
        s("url", url)
        s("version", version)
        s("whiteboard", whiteboard)
        s("work_time", work_time, float)

        add_dict("blocks", blocks_add, blocks_remove, blocks_set,
                 convert=int)
        add_dict("depends_on", depends_on_add, depends_on_remove,
                 depends_on_set, convert=int)
        add_dict("cc", cc_add, cc_remove)
        add_dict("groups", groups_add, groups_remove)
        add_dict("keywords", keywords_add, keywords_remove, keywords_set)
        add_dict("see_also", see_also_add, see_also_remove)

        if comment is not None:
            ret["comment"] = {"comment": comment}
            if comment_private:
                ret["comment"]["is_private"] = comment_private

        return ret


    ########################################
    # Methods for working with attachments #
    ########################################

    def _attachment_uri(self, attachid):
        '''Returns the URI for the given attachment ID.'''
        att_uri = self.url.replace('xmlrpc.cgi', 'attachment.cgi')
        att_uri = att_uri + '?id=%s' % attachid
        return att_uri

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
        kwargs['data'] = xmlrpclib.Binary(f.read())
        kwargs['ids'] = self._listify(idlist)

        if 'file_name' not in kwargs and hasattr(f, "name"):
            kwargs['file_name'] = os.path.basename(f.name)
        if 'content_type' not in kwargs:
            ctype = _detect_filetype(getattr(f, "name", None))
            if not ctype:
                ctype = 'application/octet-stream'
            kwargs['content_type'] = ctype

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

        headers = {}
        ret = StringIO.StringIO()

        def headers_cb(buf):
            if not ":" in buf:
                return
            name, val = buf.split(":", 1)
            headers[name.lower()] = val

        c = pycurl.Curl()
        c.setopt(pycurl.URL, att_uri)
        c.setopt(pycurl.WRITEFUNCTION, ret.write)
        c.setopt(pycurl.HEADERFUNCTION, headers_cb)
        c.setopt(pycurl.COOKIEFILE, self._cookiejar.filename or "")
        c.perform()
        c.close()

        disp = headers['content-disposition'].split(';')
        disp.pop(0)
        parms = dict([p.strip().split("=", 1) for p in disp])
        ret.name = _decode_rfc2231_value(parms['filename'])

        # Hooray, now we have a file-like object with .read() and .name
        ret.seek(0)
        return ret

    def updateattachmentflags(self, bugid, attachid, flagname, **kwargs):
        '''
        Updates a flag for the given attachment ID.
        Optional keyword args are:
            status:    new status for the flag ('-', '+', '?', 'X')
            requestee: new requestee for the flag
        '''
        update = {
            'name': flagname,
            'attach_id': int(attachid),
        }
        update.update(kwargs.items())

        result = self._proxy.Flag.update({
            'ids': [int(bugid)],
            'updates': [update]})
        return result['flag_updates'][str(bugid)]


    #####################
    # createbug methods #
    #####################

    createbug_required = ('product', 'component', 'summary', 'version',
                          'description')

    def build_createbug(self,
        product=None,
        component=None,
        version=None,
        summary=None,
        description=None,
        comment_private=None,
        blocks=None,
        cc=None,
        depends_on=None,
        groups=None,
        op_sys=None,
        platform=None,
        priority=None,
        qa_contact=None,
        resolution=None,
        severity=None,
        status=None,
        target_milestone=None,
        target_release=None,
        url=None):

        localdict = {}
        if blocks:
            localdict["blocks"] = self._listify(blocks)
        if cc:
            localdict["cc"] = self._listify(cc)
        if depends_on:
            localdict["depends_on"] = self._listify(depends_on)
        if groups:
            localdict["groups"] = self._listify(groups)
        if description:
            localdict["description"] = description
            if comment_private:
                localdict["comment_is_private"] = True

        # Most of the machinery and formatting here is the same as
        # build_update, so reuse that as much as possible
        ret = self.build_update(product=product, component=component,
                version=version, summary=summary, op_sys=op_sys,
                platform=platform, priority=priority, qa_contact=qa_contact,
                resolution=resolution, severity=severity, status=status,
                target_milestone=target_milestone,
                target_release=target_release, url=url)

        ret.update(localdict)
        return ret


    def createbug(self, *args, **kwargs):
        '''
        Create a bug with the given info. Returns a new Bug object.
        Check bugzilla API documentation for valid values, at least
        product, component, summary, version, and description need to
        be passed.
        '''
        # Previous API required users specifying keyword args that mapped
        # to the XMLRPC arg names. Maintain that bad compat, but also allow
        # receiving a single dictionary like query() does
        if kwargs and args:
            raise BugzillaError("createbug: cannot specify positional "
                                "args=%s with kwargs=%s, must be one or the "
                                "other." % (args, kwargs))
        if args:
            if len(args) > 1 or type(args[0]) is not dict:
                raise BugzillaError("createbug: positional arguments only "
                                    "accept a single dictionary.")
            data = args[0]
        else:
            data = kwargs

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

        rawbug = self._proxy.Bug.create(data)
        return _Bug(self, bug_id=rawbug["id"])


    ##############################
    # Methods for handling Users #
    ##############################

    def _getusers(self, ids=None, names=None, match=None):
        '''Return a list of users that match criteria.

        :kwarg ids: list of user ids to return data on
        :kwarg names: list of user names to return data on
        :kwarg match: list of patterns.  Returns users whose real name or
            login name match the pattern.
        :raises xmlrpclib.Fault: Code 51: if a Bad Login Name was sent to the
                names array.
            Code 304: if the user was not authorized to see user they
                requested.
            Code 505: user is logged out and can't use the match or ids
                parameter.

        Available in Bugzilla-3.4+
        '''
        params = {}
        if ids:
            params['ids'] = self._listify(ids)
        if names:
            params['names'] = self._listify(names)
        if match:
            params['match'] = self._listify(match)
        if not params:
            raise BugzillaError('_get() needs one of ids, '
                                ' names, or match kwarg.')

        return self._proxy.User.get(params)

    def getuser(self, username):
        '''Return a bugzilla User for the given username

        :arg username: The username used in bugzilla.
        :raises xmlrpclib.Fault: Code 51 if the username does not exist
        :returns: User record for the username
        '''
        ret = self.getusers(username)
        return ret and ret[0]

    def getusers(self, userlist):
        '''Return a list of Users from bugzilla.

        :userlist: List of usernames to lookup
        :returns: List of User records
        '''
        userobjs = [_User(self, **rawuser) for rawuser in
                    self._getusers(names=userlist).get('users', [])]

        # Return users in same order they were passed in
        ret = []
        for u in userlist:
            for uobj in userobjs[:]:
                if uobj.email == u:
                    userobjs.remove(uobj)
                    ret.append(uobj)
                    break
        ret += userobjs
        return ret


    def searchusers(self, pattern):
        '''Return a bugzilla User for the given list of patterns

        :arg pattern: List of patterns to match against.
        :returns: List of User records
        '''
        return [_User(self, **rawuser) for rawuser in
                self._getusers(match=pattern).get('users', [])]

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
        self._proxy.User.create(email, name, password)
        return self.getuser(email)

    def updateperms(self, user, action, groups):
        '''
        A method to update the permissions (group membership) of a bugzilla
        user.

        :arg user: The e-mail address of the user to be acted upon. Can
            also be a list of emails.
        :arg action: add, remove, or set
        :arg groups: list of groups to be added to (i.e. ['fedora_contrib'])
        '''
        groups = self._listify(groups)
        if action == "rem":
            action = "remove"
        if action not in ["add", "remove", "set"]:
            raise BugzillaError("Unknown user permission action '%s'" % action)

        update = {
            "names": self._listify(user),
            "groups": {
                action: groups,
            }
        }

        log.debug("updating user permissions:\n%s", update)
        return self._proxy.User.update(update)


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


    def adduser(self, user, name):
        '''Deprecated: Use createuser() instead.

        A method to create a user in Bugzilla. Takes the following:

        user: The email address of the user to create
        name: The full name of the user to create
        '''
        self.createuser(user, name)

    def getqueryinfo(self, force_refresh=False):
        raise NotImplementedError("getqueryinfo is deprecated and the "
                "information is not provided by any modern bugzilla.")
    querydata = property(getqueryinfo)
    querydefaults = property(getqueryinfo)
