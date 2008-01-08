# bugzilla.py - a Python interface to bugzilla.redhat.com, using xmlrpclib.
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
import os.path, base64, copy

version = '0.2'
user_agent = 'bugzilla.py/%s (Python-urllib2/%s)' % \
        (version,urllib2.__version__)

def replace_errors_with_None(r):
    '''r is a raw xmlrpc response. 
    If it represents an error, None is returned.
    Otherwise, r is returned.
    This is mostly used for XMLRPC Multicall handling.'''
    # Yes, this is a naive implementation
    # FIXME that bug_id thing is only good for getbug, but I want
    # to leave the git tree in a usable state...
    if isinstance(r,dict) and 'bug_id' in r:
        return r
    else:
        return None

class Bugzilla(object):
    '''An object which represents the data and methods exported by a Bugzilla
    instance. Uses xmlrpclib to do its thing. You'll want to create one thusly:
    bz=Bugzilla(url='https://bugzilla.redhat.com/xmlrpc.cgi',user=u,password=p)

    If you so desire, you can use cookie headers for authentication instead.
    So you could do:
    cf=glob(os.path.expanduser('~/.mozilla/firefox/default.*/cookies.txt'))
    bz=Bugzilla(url=url,cookies=cf)
    and, assuming you have previously logged info bugzilla with firefox, your
    pre-existing auth cookie would be used, thus saving you the trouble of
    stuffing your username and password in the bugzilla call.
    On the other hand, this currently munges up the cookie so you'll have to
    log back in when you next use bugzilla in firefox. So this is not
    currently recommended.

    The methods which start with a single underscore are thin wrappers around
    xmlrpc calls; those should be safe for multicall usage.
    '''
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
        self._bugfields  = None
        self._components = dict()
        self._components_details = dict()
        if 'cookies' in kwargs:
            self.readcookiefile(kwargs['cookies'])
        if 'url' in kwargs:
            self.connect(kwargs['url'])
        if 'user' in kwargs:
            self.user = kwargs['user']
        if 'password' in kwargs:
            self.password = kwargs['password']

    #---- Methods for establishing bugzilla connection and logging in

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
        self.url = url

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
        return self._proxy.bugzilla.getBugFields(self.user,self.password)
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

    def _getqueryinfo(self):
        return self._proxy.bugzilla.getQueryInfo(self.user,self.password)
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

    def _getproducts(self):
        return self._proxy.bugzilla.getProdInfo(self.user, self.password)
    def getproducts(self,force_refresh=False):
        '''Return a dict of product names and product descriptions.'''
        if force_refresh or not self._products:
            self._products = self._getproducts()
        return self._products
    # Bugzilla.products is a property - we cache the product list on the first
    # call and return it for each subsequent call.
    products = property(fget=lambda self: self.getproducts(),
                        fdel=lambda self: setattr(self,'_products',None))

    def _getcomponents(self,product):
        return self._proxy.bugzilla.getProdCompInfo(product,self.user,self.password)
    def getcomponents(self,product,force_refresh=False):
        '''Return a dict of components:descriptions for the given product.'''
        if force_refresh or product not in self._components:
            self._components[product] = self._getcomponents(product)
        return self._components[product]
    # TODO - add a .components property that acts like a dict?

    def _getcomponentsdetails(self,product):
        '''Returns a list of dicts giving details about the components in the
        given product. Each item has the following keys:
        component, description, initialowner, initialqacontact, initialcclist
        '''
        return self._proxy.bugzilla.getProdCompDetails(product,self.user,self.password)
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

    # Return raw dicts
    def _getbug(self,id):
        '''Return a dict of full bug info for the given bug id'''
        return self._proxy.bugzilla.getBug(id, self.user, self.password)
    def _getbugsimple(self,id):
        '''Return a short dict of simple bug info for the given bug id'''
        r = self._proxy.bugzilla.getBugSimple(id, self.user, self.password)
        if r and 'bug_id' not in r:
            # XXX hurr. getBugSimple doesn't fault if the bug is missing.
            # Let's synthesize one ourselves.
            raise xmlrpclib.Fault("Server","Could not load bug %s" % id)
        else:
            return r
    def _getbugs(self,idlist):
        '''Like _getbug, but takes a list of ids and returns a corresponding
        list of bug objects. Uses multicall for awesome speed.'''
        mc = self._multicall()
        for id in idlist:
            mc._getbug(id)
        raw_results = mc.run()
        del mc
        # check results for xmlrpc errors, and replace them with None
        return map(replace_errors_with_None, raw_results)
    def _getbugssimple(self,idlist):
        '''Like _getbugsimple, but takes a list of ids and returns a
        corresponding list of bug objects. Uses multicall for awesome speed.'''
        mc = self._multicall()
        for id in idlist:
            mc._getbugsimple(id)
        raw_results = mc.run()
        del mc
        # check results for xmlrpc errors, and replace them with None
        return map(replace_errors_with_None, raw_results)
    def _query(self,query):
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

    # these return Bug objects 
    def getbug(self,id):
        '''Return a Bug object with the full complement of bug data
        already loaded.'''
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

    def _addcomment(self,id,comment,private=False,
                   timestamp='',worktime='',bz_gid=''):
        '''Add a comment to the bug with the given ID. Other optional 
        arguments are as follows:
            private:   if True, mark this comment as private.
            timestamp: comment timestamp, in the form "YYYY-MM-DD HH:MM:SS"
            worktime:  amount of time spent on this comment (undoc in upstream)
            bz_gid:    if present, and the entire bug is *not* already private
                       to this group ID, this comment will be marked private.
        '''
        return self._proxy.bugzilla.addComment(id,comment,
                   self.user,self.password,private,timestamp,worktime,bz_gid)
    
    def _setstatus(self,id,status,comment='',private=False,private_in_it=False,nomail=False):
        '''Set the status of the bug with the given ID. You may optionally
        include a comment to be added, and may further choose to mark that
        comment as private.
        The status may be anything from querydefaults['bug_status_list'].
        Common statuses: 'NEW','ASSIGNED','MODIFIED','NEEDINFO'
        Less common: 'VERIFIED','ON_DEV','ON_QA','REOPENED'
        'CLOSED' is not valid with this method; use closebug() instead.
        '''
        return self._proxy.bugzilla.changeStatus(id,status,
                self.user,self.password,comment,private,private_in_it,nomail)

    def _setassignee(self,id,**data):
        '''Raw xmlrpc call to set one of the assignee fields on a bug.
        changeAssignment($id, $data, $username, $password)
        data: 'assigned_to','reporter','qa_contact','comment'
        returns: [$id, $mailresults]'''
        return self._proxy.bugzilla.changeAssignment(id,data,self.user,self.password)

    def _closebug(self,id,resolution,dupeid,fixedin,comment,isprivate,private_in_it,nomail):
        '''Raw xmlrpc call for closing bugs. Documentation from Bug.pm is
        below. Note that we drop the username and password fields because the
        Bugzilla object contains them already.

        closeBug($bugid, $new_resolution, $username, $password, $dupeid,
            $new_fixed_in, $comment, $isprivate, $private_in_it, $nomail)
        
        Close a current Bugzilla bug report with a specific resolution. This will eventually be done in Bugzilla/Bug.pm 
        instead and is meant to only be a quick fix. Please use bugzilla.changesStatus to changed to an opened state.
        This method will change the bug report's status to CLOSED.
        
            $bugid 
                # ID of bug report to add comment to.
            $new_resolution
                # Valid Bugzilla resolution to transition the report into. 
                # DUPLICATE requires $dupeid to be passed in.
            $dupeid
                # Bugzilla report ID that this bug is being closed as 
                # duplicate of. 
                # Requires $new_resolution to be DUPLICATE.
            $new_fixed_in
                # OPTIONAL String representing version of product/component 
                # that bug is fixed in.
            $comment
                # OPTIONAL Text string containing comment to add.
            $isprivate
                # OPTIONAL Whether the comment will be private to the 
                # 'private_comment' Bugzilla group. 
                # Default: false
            $private_in_it 
                # OPTIONAL if true will make the comment private in 
                # Issue Tracker
                # Default: follows $isprivate
            $nomail 
                # OPTIONAL Flag that is either 1 or 0 if you want email to be sent or not for this change
        '''
        return self._proxy.bugzilla.closeBug(id,resolution,self.user,self.password,
                dupeid,fixedin,comment,isprivate,private_in_it,nomail)

    def _updatedeps(self,id,deplist):
        #updateDepends($bug_id,$data,$username,$password,$nodependencyemail)
        #data: 'blocked'=>id,'dependson'=>id,'action' => ('add','remove')
        raise NotImplementedError

    def _updatecc(self,id,cclist,action,comment='',nomail=False):
        '''Updates the CC list using the action and account list specified.
        cclist must be a list (not a tuple!) of addresses.
        action may be 'add', 'remove', or 'makeexact'.
        comment specifies an optional comment to add to the bug.
        if mail is True, email will be generated for this change.
        '''
        data = {'id':id, 'action':action, 'cc':','.join(cclist),
                'comment':comment, 'nomail':nomail}
        return self._proxy.bugzilla.updateCC(data,self.user,self.password)

    def _updatewhiteboard(self,id,text,which,action):
        '''Update the whiteboard given by 'which' for the given bug.
        performs the given action (which may be 'append',' prepend', or 
        'overwrite') using the given text.'''
        data = {'type':which,'text':text,'action':action}
        return self._proxy.bugzilla.updateWhiteboard(id,data,self.user,self.password)

    # TODO: update this when the XMLRPC interface grows requestee support
    def _updateflags(self,id,flags):
        '''Updates the flags associated with a bug report.
        data should be a hash of {'flagname':'value'} pairs, like so:
        {'needinfo':'?','fedora-cvs':'+'}
        You may also add a "nomail":1 item, which will suppress email if set.

        NOTE: the Red Hat XMLRPC interface does not yet support setting the
        requestee (as in: needinfo from smartguy@answers.com). Alas.'''
        return self._proxy.bugzilla.updateFlags(id,flags,self.user,self.password)

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
        (attachid, mailresults) = self._proxy.bugzilla.addAttachment(id,kwargs,self.user,self.password)
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

    #---- createbug - big complicated call to create a new bug

    def _createbug(self,**data):
        '''Raw xmlrpc call for createBug() Doesn't bother guessing defaults
        or checking argument validity. Use with care.
        Returns [bug_id, mailresults]'''
        return self._proxy.bugzilla.createBug(data,self.user,self.password)

    def createbug(self,check_args=False,**data):
        '''Create a bug with the given info. Returns the bug ID.
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
        required = ('product','component','version','short_desc','comment',
                    'rep_platform','bug_severity','op_sys','bug_file_loc')
        # The xmlrpc will raise an error if one of these is missing, but
        # let's try to save a network roundtrip here if possible..
        for i in required:
            if i not in data or not data[i]:
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
        [bug_id, mail_results] = self._createbug(**data)
        return Bug(self,bug_id=bug_id)
        # Trivia: this method has ~5.8 lines of comment per line of code. Yow!

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
            self.__dict__.update(kwargs['dict'])
        if 'bug_id' in kwargs:
            setattr(self,'bug_id',kwargs['bug_id'])
        if 'autorefresh' in kwargs:
            self.autorefresh = kwargs['autorefresh']
        # No bug_id? this bug is invalid!
        if not hasattr(self,'bug_id'):
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
        else:
            desc = self.short_desc
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
        # FIXME reload bug data here

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
        # FIXME reload bug data here
        return r
    def addcomment(self,comment,private=False,timestamp='',worktime='',bz_gid=''):
        '''Add the given comment to this bug. Set private to True to mark this
        comment as private. You can also set a timestamp for the comment, in
        "YYYY-MM-DD HH:MM:SS" form. Worktime is undocumented upstream.
        If bz_gid is set, and the entire bug is not already private to that
        group, this comment will be private.'''
        self.bugzilla._addcomment(self.bug_id,comment,private,timestamp,
                                  worktime,bz_gid)
        # FIXME reload bug data here
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
        # FIXME reload bug data here
    def _dowhiteboard(self,text,which,action):
        '''Actually does the updateWhiteboard call to perform the given action
        (append,prepend,overwrite) with the given text on the given whiteboard
        for the given bug.'''
        self.bugzilla._updatewhiteboard(self.bug_id,text,which,action)
        # FIXME reload bug data here

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
# TODO: add a sync() method that writes the changed data in the Bug object
# back to Bugzilla. Someday.
