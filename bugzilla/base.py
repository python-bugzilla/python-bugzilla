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

import locale
import os
import sys

from io import BytesIO

if hasattr(sys.version_info, "major") and sys.version_info.major >= 3:
    # pylint: disable=F0401,E0611
    from configparser import SafeConfigParser
    from http.cookiejar import LoadError, LWPCookieJar, MozillaCookieJar
    from urllib.parse import urlparse, parse_qsl
    from xmlrpc.client import (
        Binary, Fault, ProtocolError, ServerProxy, Transport)
else:
    from ConfigParser import SafeConfigParser
    from cookielib import LoadError, LWPCookieJar, MozillaCookieJar
    from urlparse import urlparse, parse_qsl
    from xmlrpclib import (
        Binary, Fault, ProtocolError, ServerProxy, Transport)

import requests

from bugzilla import __version__, log
from bugzilla.bug import _Bug, _User


# Backwards compatibility
Bug = _Bug

mimemagic = None


def _detect_filetype(fname):
    # pylint: disable=E1103
    # E1103: Instance of 'bool' has no '%s' member
    # pylint confuses mimemagic to be of type 'bool'
    global mimemagic

    if mimemagic is None:
        try:
            # pylint: disable=F0401
            # F0401: Unable to import 'magic' (import-error)
            import magic
            mimemagic = magic.open(getattr(magic, "MAGIC_MIME_TYPE", 16))
            mimemagic.load()
        except ImportError:
            e = sys.exc_info()[1]
            log.debug("Could not load python-magic: %s", e)
            mimemagic = False
    if mimemagic is False:
        return None

    if not os.path.isabs(fname):
        return None

    try:
        return mimemagic.file(fname)
    except Exception:
        e = sys.exc_info()[1]
        log.debug("Could not detect content_type: %s", e)
    return None


def _build_cookiejar(cookiefile):
    cj = MozillaCookieJar(cookiefile)
    if cookiefile is None:
        return cj
    if not os.path.exists(cookiefile):
        # Make sure a new file has correct permissions
        open(cookiefile, 'a').close()
        os.chmod(cookiefile, 0o600)
        cj.save()
        return cj

    # We always want to use Mozilla cookies, but we previously accepted
    # LWP cookies. If we see the latter, convert it to former
    try:
        cj.load()
        return cj
    except LoadError:
        pass

    try:
        cj = LWPCookieJar(cookiefile)
        cj.load()
    except LoadError:
        raise BugzillaError("cookiefile=%s not in LWP or Mozilla format" %
                            cookiefile)

    retcj = MozillaCookieJar(cookiefile)
    for cookie in cj:
        retcj.set_cookie(cookie)
    retcj.save()
    return retcj


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


class RequestsTransport(Transport):
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
            response = requests.post(
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


class BugzillaError(Exception):
    '''Error raised in the Bugzilla client code.'''
    pass


class _FieldAlias(object):
    """
    Track API attribute names that differ from what we expose in users.

    For example, originally 'short_desc' was the name of the property that
    maps to 'summary' on modern bugzilla. We want pre-existing API users
    to be able to continue to use Bug.short_desc, and
    query({"short_desc": "foo"}). This class tracks that mapping.

    @oldname: The old attribute name
    @newname: The modern attribute name
    @is_api: If True, use this mapping for values sent to the xmlrpc API
        (like the query example)
    @is_bug: If True, use this mapping for Bug attribute names.
    """
    def __init__(self, newname, oldname, is_api=True, is_bug=True):
        self.newname = newname
        self.oldname = oldname
        self.is_api = is_api
        self.is_bug = is_bug


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

    # bugzilla version that the class is targetting. filled in by
    # subclasses
    bz_ver_major = 0
    bz_ver_minor = 0

    # Intended to be the API version of the class, but historically is
    # unused and basically worthless since we don't plan on breaking API.
    version = "0.1"

    @staticmethod
    def url_to_query(url):
        '''
        Given a big huge bugzilla query URL, returns a query dict that can
        be passed along to the Bugzilla.query() method.
        '''
        q = {}

        # pylint: disable=unpacking-non-sequence
        (ignore, ignore, path,
         ignore, query, ignore) = urlparse(url)

        base = os.path.basename(path)
        if base not in ('buglist.cgi', 'query.cgi'):
            return {}

        for (k, v) in parse_qsl(query):
            if k not in q:
                q[k] = v
            elif isinstance(q[k], list):
                q[k].append(v)
            else:
                oldv = q[k]
                q[k] = [oldv, v]

        # Handle saved searches
        if base == "buglist.cgi" and "namedcmd" in q and "sharer_id" in q:
            q = {
                "sharer_id": q["sharer_id"],
                "savedsearch": q["namedcmd"],
            }

        return q

    @staticmethod
    def fix_url(url):
        """
        Turn passed url into a bugzilla XMLRPC web url
        """
        if '://' not in url:
            log.debug('No scheme given for url, assuming https')
            url = 'https://' + url
        if url.count('/') < 3:
            log.debug('No path given for url, assuming /xmlrpc.cgi')
            url = url + '/xmlrpc.cgi'
        return url

    def __init__(self, url=None, user=None, password=None, cookiefile=-1,
                 sslverify=True, tokenfile=-1):
        # Hook to allow Bugzilla autodetection without weirdly overriding
        # __init__
        if self._init_class_from_url(url, sslverify):
            kwargs = locals().copy()
            del(kwargs["self"])

            # pylint: disable=non-parent-init-called
            self.__class__.__init__(self, **kwargs)
            return

        # Settings the user might want to tweak
        self.user = user or ''
        self.password = password or ''
        self.url = ''

        self._transport = None
        self._cookiejar = None
        self._sslverify = bool(sslverify)

        self.logged_in = False
        self.bug_autorefresh = True

        # Bugzilla object state info that users shouldn't mess with
        self._proxy = None
        self._products = None
        self._bugfields = None
        self._components = {}
        self._components_details = {}
        self._init_private_data()

        if cookiefile == -1:
            cookiefile = os.path.expanduser('~/.bugzillacookies')
        if tokenfile == -1:
            tokenfile = os.path.expanduser("~/.bugzillatoken")
        log.debug("Using tokenfile=%s", tokenfile)
        self.cookiefile = cookiefile
        self.tokenfile = tokenfile

        # List of field aliases. Maps old style RHBZ parameter
        # names to actual upstream values. Used for createbug() and
        # query include_fields at least.
        self._field_aliases = []
        self._add_field_alias('summary', 'short_desc')
        self._add_field_alias('description', 'comment')
        self._add_field_alias('platform', 'rep_platform')
        self._add_field_alias('severity', 'bug_severity')
        self._add_field_alias('status', 'bug_status')
        self._add_field_alias('id', 'bug_id')
        self._add_field_alias('blocks', 'blockedby')
        self._add_field_alias('blocks', 'blocked')
        self._add_field_alias('depends_on', 'dependson')
        self._add_field_alias('creator', 'reporter')
        self._add_field_alias('url', 'bug_file_loc')
        self._add_field_alias('dupe_of', 'dupe_id')
        self._add_field_alias('dupe_of', 'dup_id')
        self._add_field_alias('comments', 'longdescs')
        self._add_field_alias('creation_time', 'opendate')
        self._add_field_alias('creation_time', 'creation_ts')
        self._add_field_alias('whiteboard', 'status_whiteboard')
        self._add_field_alias('last_change_time', 'delta_ts')

        if url:
            self.connect(url)

    def _init_class_from_url(self, url, sslverify):
        ignore = url
        ignore = sslverify

    def _init_private_data(self):
        '''initialize private variables used by this bugzilla instance.'''
        self._proxy = None
        self._products = None
        self._bugfields = None
        self._components = {}
        self._components_details = {}

    def _get_user_agent(self):
        ret = ('Python-urllib bugzilla.py/%s %s' %
               (__version__, str(self.__class__.__name__)))
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

    def _add_field_alias(self, *args, **kwargs):
        self._field_aliases.append(_FieldAlias(*args, **kwargs))

    def _get_bug_aliases(self):
        return [(f.newname, f.oldname)
                for f in self._field_aliases if f.is_bug]

    def _get_api_aliases(self):
        return [(f.newname, f.oldname)
                for f in self._field_aliases if f.is_api]


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
        if not configpath:
            configpath = self.configpath
        configpath = [os.path.expanduser(p) for p in configpath]
        c = SafeConfigParser()
        r = c.read(configpath)
        if not r:
            return
        # See if we have a config section that matches this url.
        section = ""
        # Substring match - prefer the longest match found
        log.debug("Searching for config section matching %s", self.url)
        for s in sorted(c.sections()):
            if s in self.url:
                log.debug("Found matching section: %s", s)
                section = s
        if not section:
            return
        for k, v in c.items(section):
            if k in ('user', 'password'):
                log.debug("Setting '%s' from configfile", k)
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

        self._transport = RequestsTransport(
            url, self._cookiejar, sslverify=self._sslverify)
        self._transport.user_agent = self.user_agent
        self._proxy = _BugzillaServerProxy(url, self.tokenfile,
            self._transport)

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
        is not set, ValueError will be raised. If login fails, BugzillaError
        will be raised.

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
            ret = self._login(self.user, self.password)
            self.logged_in = True
            self.password = ''
            log.info("login successful for user=%s", self.user)
            return ret
        except Fault:
            e = sys.exc_info()[1]
            raise BugzillaError("Login failed: %s" % str(e.faultString))

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
        raise RuntimeError("This bugzilla version does not support listing "
            "bug fields.")

    def getbugfields(self, force_refresh=False):
        '''
        Calls getBugFields, which returns a list of fields in each bug
        for this bugzilla instance. This can be used to set the list of attrs
        on the Bug object.
        '''
        if force_refresh or self._bugfields is None:
            log.debug("Refreshing bugfields")
            self._bugfields = self._getbugfields()
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
        if self._products is None:
            self._products = []

        for product in self._getproductinfo(**kwargs):
            added = False
            for current in self._products[:]:
                if (current.get("id", -1) != product.get("id", -2) and
                    current.get("name", -1) != product.get("name", -2)):
                    continue

                self._products.remove(current)
                self._products.append(product)
                added = True
                break
            if not added:
                self._products.append(product)

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
        log.debug("Calling Component.create with: %s", data)
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
        log.debug("Calling Component.update with: %s", data)
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
        log.debug("Calling Product.get_products with: %s", kwargs)
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
        if self._products is None:
            self._products = []

        def _find_comps():
            for p in self._products:
                if p["name"] != product:
                    continue
                return p.get("components", None)

        comps = _find_comps()
        if comps is None:
            self.refresh_products(names=[product],
                                  include_fields=["name", "id", "components"])
            comps = _find_comps()

        if comps is None:
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
    _getbug_extra_fields = []
    _supports_getbug_extra_fields = False

    def _getbugs(self, idlist, simple=False, permissive=True,
            include_fields=None, exclude_fields=None, extra_fields=None):
        '''
        Return a list of dicts of full bug info for each given bug id.
        bug ids that couldn't be found will return None instead of a dict.

        @simple: If True, don't ask for any large extra_fields.
        '''
        oldidlist = idlist
        idlist = []
        for i in oldidlist:
            try:
                idlist.append(int(i))
            except ValueError:
                # String aliases can be passed as well
                idlist.append(i)

        extra_fields = self._listify(extra_fields or [])
        if not simple:
            extra_fields += self._getbug_extra_fields

        getbugdata = {"ids": idlist}
        if permissive:
            getbugdata["permissive"] = 1
        if self.bz_ver_major >= 4:
            if include_fields:
                getbugdata["include_fields"] = self._listify(include_fields)
            if exclude_fields:
                getbugdata["exclude_fields"] = self._listify(exclude_fields)
        if self._supports_getbug_extra_fields:
            getbugdata["extra_fields"] = extra_fields

        log.debug("Calling Bug.get_bugs with: %s", getbugdata)
        r = self._proxy.Bug.get_bugs(getbugdata)

        if self.bz_ver_major >= 4:
            bugdict = dict([(b['id'], b) for b in r['bugs']])
        else:
            bugdict = dict([(b['id'], b['internals']) for b in r['bugs']])

        ret = []
        for i in idlist:
            found = None
            if i in bugdict:
                found = bugdict[i]
            else:
                # Need to map an alias
                for valdict in bugdict.values():
                    if i in valdict.get("alias", []):
                        found = valdict
                        break

            ret.append(found)

        return ret

    def _getbug(self, objid, simple=False,
            include_fields=None, exclude_fields=None, extra_fields=None):
        '''Return a dict of full bug info for the given bug id'''
        return self._getbugs([objid], simple=simple, permissive=False,
            include_fields=include_fields, exclude_fields=exclude_fields,
            extra_fields=extra_fields)[0]

    def getbug(self, objid,
            include_fields=None, exclude_fields=None, extra_fields=None):
        '''Return a Bug object with the full complement of bug data
        already loaded.'''
        data = self._getbug(objid, include_fields=include_fields,
            exclude_fields=exclude_fields, extra_fields=extra_fields)
        return _Bug(self, dict=data, autorefresh=self.bug_autorefresh)

    def getbugs(self, idlist,
        include_fields=None, exclude_fields=None, extra_fields=None):
        '''Return a list of Bug objects with the full complement of bug data
        already loaded. If there's a problem getting the data for a given id,
        the corresponding item in the returned list will be None.'''
        data = self._getbugs(idlist, include_fields=include_fields,
            exclude_fields=exclude_fields, extra_fields=extra_fields)
        return [(b and _Bug(self, dict=b,
                            autorefresh=self.bug_autorefresh)) or None
                for b in data]

    # Since for so long getbugsimple was just getbug, I don't think we can
    # remove any fields without possibly causing a slowdown for some
    # existing users. Just have this API mean 'don't ask for the extra
    # big stuff'
    def getbugsimple(self, objid):
        '''Return a Bug object given bug id, populated with simple info'''
        return _Bug(self,
                    dict=self._getbug(objid, simple=True),
                    autorefresh=self.bug_autorefresh)

    def getbugssimple(self, idlist):
        '''Return a list of Bug objects for the given bug ids, populated with
        simple info. As with getbugs(), if there's a problem getting the data
        for a given bug ID, the corresponding item in the returned list will
        be None.'''
        return [(b and _Bug(self, dict=b,
                autorefresh=self.bug_autorefresh)) or None
                for b in self._getbugs(idlist, simple=True)]


    #################
    # query methods #
    #################

    def _convert_include_field_list(self, _in):
        if not _in:
            return _in

        for newname, oldname in self._get_api_aliases():
            if oldname in _in:
                _in.remove(oldname)
                if newname not in _in:
                    _in.append(newname)
        return _in

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
                    include_fields=None,
                    quicksearch=None,
                    savedsearch=None,
                    savedsearch_sharer_id=None,
                    sub_component=None,
                    tags=None):
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
        ignore = emailtype
        ignore = booleantype
        ignore = include_fields

        for key, val in [
            ('fixed_in', fixed_in),
            ('blocked', blocked),
            ('dependson', dependson),
            ('flag', flag),
            ('qa_whiteboard', qa_whiteboard),
            ('devel_whiteboard', devel_whiteboard),
            ('alias', alias),
            ('boolean_query', boolean_query),
            ('long_desc', long_desc),
            ('quicksearch', quicksearch),
            ('savedsearch', savedsearch),
            ('sharer_id', savedsearch_sharer_id),
            ('sub_component', sub_component),
        ]:
            if val is not None:
                raise RuntimeError("'%s' search not supported by this "
                                   "bugzilla" % key)

        query = {
            "product": self._listify(product),
            "component": self._listify(component),
            "version": version,
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
            "tag": self._listify(tags),
        }

        # Strip out None elements in the dict
        for k, v in query.copy().items():
            if v is None:
                del(query[k])
        return query

    def _query(self, query):
        # This is kinda redundant now, but various scripts call
        # _query with their own assembled dictionaries, so don't
        # drop this lest we needlessly break those users
        log.debug("Calling Bug.search with: %s", query)
        return self._proxy.Bug.search(query)

    def query(self, query):
        '''Query bugzilla and return a list of matching bugs.
        query must be a dict with fields like those in in querydata['fields'].
        Returns a list of Bug objects.
        Also see the _query() method for details about the underlying
        implementation.
        '''
        r = self._query(query)
        log.debug("Query returned %s bugs", len(r['bugs']))
        return [_Bug(self, dict=b,
                autorefresh=self.bug_autorefresh) for b in r['bugs']]

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

        log.debug("Calling Bug.update with: %s", tmp)
        return self._proxy.Bug.update(tmp)

    def update_flags(self, idlist, flags):
        '''
        Updates the flags associated with a bug report.
        Format of flags is:
        [{"name": "needinfo", "status": "+", "requestee": "foo@bar.com"},
         {"name": "devel_ack", "status": "-"}, ...]
        '''
        d = {"ids": self._listify(idlist), "updates": flags}
        log.debug("Calling Flag.update with: %s", d)
        return self._proxy.Flag.update(d)

    def update_tags(self, idlist, tags_add=None, tags_remove=None):
        '''
        Updates the 'tags' field for a bug.
        '''
        tags = {}
        if tags_add:
            tags["add"] = self._listify(tags_add)
        if tags_remove:
            tags["remove"] = self._listify(tags_remove)

        d = {
            "ids": self._listify(idlist),
            "tags": tags,
        }

        log.debug("Calling Bug.update_tags with: %s", d)
        return self._proxy.Bug.update_tags(d)


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
                     internal_whiteboard=None,
                     sub_component=None):
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
            ("sub_component", sub_component),
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
        or raises XMLRPC Fault if something goes wrong.

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

        data = f.read()
        if not isinstance(data, bytes):
            data = data.encode(locale.getpreferredencoding())
        kwargs['data'] = Binary(data)

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

        def get_filename(headers):
            import re

            match = re.search(
                r'^.*filename="?(.*)"$',
                headers.get('content-disposition', '')
            )

            # default to attchid if no match was found
            return match.group(1) if match else attachid

        att_uri = self._attachment_uri(attachid)

        response = requests.get(att_uri, cookies=self._cookiejar, stream=True)

        ret = BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                ret.write(chunk)
        ret.name = get_filename(response.headers)

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
        assigned_to=None,
        keywords=None,
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
        url=None,
        sub_component=None):

        localdict = {}
        if blocks:
            localdict["blocks"] = self._listify(blocks)
        if cc:
            localdict["cc"] = self._listify(cc)
        if depends_on:
            localdict["depends_on"] = self._listify(depends_on)
        if groups:
            localdict["groups"] = self._listify(groups)
        if keywords:
            localdict["keywords"] = self._listify(keywords)
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
                target_release=target_release, url=url,
                assigned_to=assigned_to, sub_component=sub_component)

        ret.update(localdict)
        return ret

    def _validate_createbug(self, *args, **kwargs):
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

        # If we're getting a call that uses an old fieldname, convert it to the
        # new fieldname instead.
        for newname, oldname in self._get_api_aliases():
            if (newname in self.createbug_required and
                newname not in data and
                oldname in data):
                data[newname] = data.pop(oldname)

        # Back compat handling for check_args
        if "check_args" in data:
            del(data["check_args"])

        return data

    def createbug(self, *args, **kwargs):
        '''
        Create a bug with the given info. Returns a new Bug object.
        Check bugzilla API documentation for valid values, at least
        product, component, summary, version, and description need to
        be passed.
        '''
        data = self._validate_createbug(*args, **kwargs)
        log.debug("Calling Bug.create with: %s", data)
        rawbug = self._proxy.Bug.create(data)
        return _Bug(self, bug_id=rawbug["id"],
                    autorefresh=self.bug_autorefresh)


    ##############################
    # Methods for handling Users #
    ##############################

    def _getusers(self, ids=None, names=None, match=None):
        '''Return a list of users that match criteria.

        :kwarg ids: list of user ids to return data on
        :kwarg names: list of user names to return data on
        :kwarg match: list of patterns.  Returns users whose real name or
            login name match the pattern.
        :raises XMLRPC Fault: Code 51: if a Bad Login Name was sent to the
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

        log.debug("Calling User.get with: %s", params)
        return self._proxy.User.get(params)

    def getuser(self, username):
        '''Return a bugzilla User for the given username

        :arg username: The username used in bugzilla.
        :raises XMLRPC Fault: Code 51 if the username does not exist
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
        :raises XMLRPC Fault: Code 501 if the username already exists
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

        log.debug("Call User.update with: %s", update)
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
        ignore = force_refresh
        raise RuntimeError("getqueryinfo is deprecated and the "
            "information is not provided by any modern bugzilla.")
    querydata = property(getqueryinfo)
    querydefaults = property(getqueryinfo)
