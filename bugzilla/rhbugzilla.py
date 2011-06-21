# rhbugzilla.py - a Python interface to Red Hat Bugzilla using xmlrpclib.
#
# Copyright (C) 2008, 2009 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import bugzilla.base
from bugzilla.bugzilla3 import Bugzilla3, Bugzilla34
import copy, xmlrpclib

class RHBugzilla(bugzilla.base.BugzillaBase):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by Red Hat's Bugzilla 2.18 variant.

    RHBugzilla supports XMLRPC MultiCall. The methods which start with a
    single underscore are thin wrappers around XMLRPC methods and should thus
    be safe for multicall use.

    Documentation for most of these methods can be found here:
    https://bugzilla.redhat.com/docs/en/html/api/extensions/RedHat/lib/WebService/CompatBugzilla.html
    '''

    version = '0.3'
    user_agent = bugzilla.base.user_agent + ' RHBugzilla/%s' % version

    def __init__(self,**kwargs):
        bugzilla.base.BugzillaBase.__init__(self,**kwargs)
        self.user_agent = self.__class__.user_agent

    def _login(self,user,password):
        '''Backend login method for RHBugzilla.'''
        return self._proxy.bugzilla.login(user,password)

    def _logout(self):
        '''Backend logout method for RHBugzilla.'''
        # "Logouts are not implemented due to the non-session nature of
        # XML-RPC communication."
        # That's funny, since we get a (session-based) login cookie...
        return True

    #---- Methods and properties with basic bugzilla info

    def _multicall(self):
        '''This returns kind of a mash-up of the Bugzilla object and the
        xmlrpclib.MultiCall object. Methods you call on this object will be
        added to the MultiCall queue, but they will return None. When you're
        ready, call the run() method and all the methods in the queue will be
        run and the results of each will be returned in a list. So, for example:

        mc = bz._multicall()
        mc._getbug(1)
        mc._getbug(1337)
        mc._query({'component':'glibc','product':'Fedora','version':'devel'})
        (bug1, bug1337, queryresult) = mc.run()

        Note that you should only use the raw xmlrpc calls (mostly the methods
        starting with an underscore). Normal getbug(), for example, tries to
        return a _Bug object, but with the multicall object it'll end up empty
        and, therefore, useless.

        Further note that run() returns a list of raw xmlrpc results; you'll
        need to wrap the output in Bug objects yourself if you're doing that
        kind of thing. For example, Bugzilla.getbugs() could be implemented:

        mc = self._multicall()
        for id in idlist:
            mc._getbug(id)
        rawlist = mc.run()
        return [_Bug(self,dict=b) for b in rawlist]
        '''
        mc = copy.copy(self)
        mc._proxy = xmlrpclib.MultiCall(self._proxy)
        def run(): return mc._proxy().results
        mc.run = run
        return mc

    # Connect the backend methods to the XMLRPC methods
    def _getbugfields(self):
        return self._proxy.bugzilla.getBugFields()
    def _getqueryinfo(self):
        return self._proxy.bugzilla.getQueryInfo()
    def _getproducts(self):
        '''Backend _getproducts method for RH Bugzilla. This predates the
        Bugzilla3 Products stuff, so we need to massage this data to make it
        fit the proper format'''
        r = self._proxy.bugzilla.getProdInfo()
        n = 0
        prod = []
        for name,desc in r.iteritems():
            # We're making up a fake id, since RHBugzilla doesn't use them
            prod.append({'id':n,'name':name,'description':desc})
            n += 1
        return prod
    def _getcomponents(self,product):
        if type(product) == int:
            product = self._product_id_to_name(product)
        return self._proxy.bugzilla.getProdCompInfo(product)
    def _getcomponentsdetails(self,product):
        if type(product) == int:
            product = self._product_id_to_name(product)
        return self._proxy.bugzilla.getProdCompDetails(product)
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
        '''Return a dict of full bug info for the given bug id'''
        return self._proxy.bugzilla.getBug(id)
    def _getbugsimple(self,id):
        '''Return a short dict of simple bug info for the given bug id'''
        r = self._proxy.bugzilla.getBugSimple(id)
        if r and 'bug_id' not in r:
            # XXX hurr. getBugSimple doesn't fault if the bug is missing.
            # Let's synthesize one ourselves.
            raise xmlrpclib.Fault("Server","Could not load bug %s" % id)
        else:
            return r
    # Multicall methods
    def _getbugs(self,idlist):
        '''Like _getbug, but takes a list of ids and returns a corresponding
        list of bug objects. Uses multicall for awesome speed.'''
        mc = self._multicall()
        for id in idlist:
            mc._getbug(id)
        raw_results = mc.run()
        del mc
        # check results for xmlrpc errors, and replace them with None
        return bugzilla.base.replace_getbug_errors_with_None(raw_results)
    def _getbugssimple(self,idlist):
        '''Like _getbugsimple, but takes a list of ids and returns a
        corresponding list of bug objects. Uses multicall for awesome speed.'''
        mc = self._multicall()
        for id in idlist:
            mc._getbugsimple(id)
        raw_results = mc.run()
        del mc
        # check results for xmlrpc errors, and replace them with None
        return bugzilla.base.replace_getbug_errors_with_None(raw_results)

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
        return self._proxy.bugzilla.runQuery(query)

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
        return self._proxy.bugzilla.addComment(id,comment,self.user,'',
                private,timestamp,worktime,bz_gid)
    def _setstatus(self,id,status,comment='',private=False,private_in_it=False,nomail=False):
        '''Set the status of the bug with the given ID. You may optionally
        include a comment to be added, and may further choose to mark that
        comment as private.
        The status may be anything from querydefaults['bug_status_list'].
        Common statuses: 'NEW','ASSIGNED','MODIFIED','NEEDINFO'
        Less common: 'VERIFIED','ON_DEV','ON_QA','REOPENED'
        'CLOSED' is not valid with this method; use closebug() instead.
        '''
        return self._proxy.bugzilla.changeStatus(id,status,self.user,'',
                comment,private,private_in_it,nomail)
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
        return self._proxy.bugzilla.closeBug(id,resolution,self.user,'',
                dupeid,fixedin,comment,isprivate,private_in_it,nomail)
    def _setassignee(self,id,**data):
        '''Raw xmlrpc call to set one of the assignee fields on a bug.
        changeAssignment($id, $data, $username, $password)
        data: 'assigned_to','reporter','qa_contact','comment'
        returns: [$id, $mailresults]'''
        return self._proxy.bugzilla.changeAssignment(id,data)
    def _updatedeps(self,id,blocked,dependson,action):
        '''update the deps (blocked/dependson) for the given bug.
        blocked/dependson: list of bug ids/aliases
        action: 'add' or 'delete'

        RHBZ call:
        updateDepends($bug_id,$data,$username,$password,$nodependencyemail)
        #data: 'blocked'=>id,'dependson'=>id,'action' => ('add','remove')

        RHBZ only does one bug at a time, so this method will loop through
        the blocked/dependson lists. This may be slow.
        '''
        r = []
        # Massage input to match what RHBZ expects
        if action == 'delete':
            action == 'remove'
        data = {'id':id, 'action':action, 'blocked':'', 'dependson':''}
        for b in blocked:
            data['blocked'] = b
            self._proxy.bugzilla.updateDepends(id,data)
        data['blocked'] = ''
        for d in dependson:
            data['dependson'] = d
            self._proxy.bugzilla.updateDepends(id,data)
    def _updatecc(self,id,cclist,action,comment='',nomail=False):
        '''Updates the CC list using the action and account list specified.
        cclist must be a list (not a tuple!) of addresses.
        action may be 'add', 'delete', or 'overwrite'.
        comment specifies an optional comment to add to the bug.
        if mail is True, email will be generated for this change.
        '''
        # Massage the 'action' param into what the old updateCC call expects
        if action == 'delete':
            action = 'remove'
        elif action == 'overwrite':
            action = 'makeexact'
        data = {'id':id, 'action':action, 'cc':','.join(cclist),
                'comment':comment, 'nomail':nomail}
        return self._proxy.bugzilla.updateCC(data)
    def _updatewhiteboard(self,id,text,which,action,comment,private):
        '''Update the whiteboard given by 'which' for the given bug.
        performs the given action (which may be 'append',' prepend', or
        'overwrite') using the given text.'''
        data = {'type':which,'text':text,'action':action}
        if comment is not None:
            data['comment'] = comment
            if private:
                data['commentprivacy'] = True
        return self._proxy.bugzilla.updateWhiteboard(id,data)
    # TODO: update this when the XMLRPC interface grows requestee support
    def _updateflags(self,id,flags):
        '''Updates the flags associated with a bug report.
        data should be a hash of {'flagname':'value'} pairs, like so:
        {'needinfo':'?','fedora-cvs':'+'}
        You may also add a "nomail":1 item, which will suppress email if set.

        NOTE: the Red Hat XMLRPC interface does not yet support setting the
        requestee (as in: needinfo from smartguy@answers.com). Alas.'''
        return self._proxy.bugzilla.updateFlags(id,flags)

    #---- Methods for working with attachments

    # If your bugzilla wants attachments in something other than base64, you
    # should override _attachment_encode here.
    # If your bugzilla uses non-standard paths for attachment.cgi, you'll
    # want to override _attachment_uri here.

    def _attachfile(self,id,**attachdata):
        return self._proxy.bugzilla.addAttachment(id,attachdata)

    #---- createbug - call to create a new bug

    def _createbug(self,**data):
        '''Raw xmlrpc call for createBug() Doesn't bother guessing defaults
        or checking argument validity. Use with care.
        Returns bug_id'''
        r = self._proxy.bugzilla.createBug(data)
        return r[0]
    # Methods for updating a user
    def _updateperms(self,user,action,groups):
        r = self._proxy.bugzilla.updatePerms(user, action, groups, self.user,
                self.password)
        return r
    def _adduser(self,user,name):
        r = self._proxy.bugzilla.addUser(user, name, self.user, self.password)
        return r
    def _addcomponent(self,data):
        add_required_fields = ('product','component','initialowner','description')
        for field in add_required_fields:
            if field not in data or not data[field]:
                raise TypeError, "mandatory fields missing: %s" % field
        if type(data['product']) == int:
            data['product'] = self._product_id_to_name(data['product'])
        r = self._proxy.bugzilla.addComponent(data,self.user,self.password)
        return r
    def _editcomponent(self,data):
        edit_required_fields = ('initialowner','product','component')
        for field in edit_required_fields:
            if field not in data or not data[field]:
                raise TypeError, "mandatory field missing: %s" % field
        if type(data['product']) == int:
            data['product'] = self._product_id_to_name(data['product'])
        r = self._proxy.bugzilla.editComponent(data,self.user,self.password)
        return r

class RHBugzilla3(Bugzilla34, RHBugzilla):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by Red Hat's Bugzilla 3.4+ instance, which is a superset
    of the Bugzilla 3.4 methods. The additional methods (e.g. Bug.update)
    should make their way into a later upstream Bugzilla release.

    Note that RHBZ3 *also* supports most of the old RHBZ methods, under the
    'bugzilla' namespace, so we use those when BZ3 methods aren't available.

    This class was written using bugzilla.redhat.com's API docs:
    https://bugzilla.redhat.com/docs/en/html/api/

    By default, _getbugs will multicall getBug(id) multiple times, rather than
    doing a single Bug.get(idlist) call. You can disable this behavior by
    setting the 'multicall' property to False. This will make it somewhat
    faster, but any missing/unreadable bugs will cause the entire call to
    Fault rather than returning any data.
    '''

    version = '0.2'
    user_agent = bugzilla.base.user_agent + ' RHBugzilla3/%s' % version

    def __init__(self,**kwargs):
        super(RHBugzilla3, self).__init__(**kwargs)
        self.user_agent = self.__class__.user_agent
        self.multicall = kwargs.get('multicall',True)

    # XXX it'd be nice if this wasn't just a copy of RHBugzilla's _getbugs
    def _getbugs(self,idlist):
        r = []
        if self.multicall:
            if len(idlist) == 1:
                return [self._proxy.bugzilla.getBug(idlist[0])]
            mc = self._multicall()
            for id in idlist:
                mc._proxy.bugzilla.getBug(id)
            raw_results = mc.run()
            del mc
            # check results for xmlrpc errors, and replace them with None
            r = bugzilla.base.replace_getbug_errors_with_None(raw_results)
        else:
            raw_results = self._proxy.Bug.get({'ids':idlist})
            r = [i['internals'] for i in raw_results['bugs']]
        return r

    # This can be removed once RHBZ supports BZ3.6's Bug.fields() method
    _getbugfields = RHBugzilla._getbugfields
    # Use the upstream versions of these methods rather than the RHBZ ones
    _query = Bugzilla34._query
    # This can be activated once Bug.get() returns all the data that
    # RHBZ's getBug() does.
    #_getbugs = Bugzilla3._getbugs # Also _getbug, _getbugsimple, etc.

    #---- Methods for updating bugs.

    def _update_bugs(self,ids,updates):
        '''Update the given fields with the given data in one or more bugs.
        ids should be a list of integers or strings, representing bug ids or
        aliases.
        updates is a dict containing pairs like so: {'fieldname':'newvalue'}
        '''
        # TODO document changeable fields & return values
        # TODO I think we need to catch XMLRPC exceptions to get a useful
        # return value
        # NOTE: this will be moved to upstream Bugzilla someday
        return self._proxy.Bug.update({'ids':ids,'updates':updates})

    def _update_bug(self,id,updates):
        '''Update a single bug, specified by integer ID or (string) bug alias.
        Really just a convenience method for _update_bugs(ids=[id],updates)'''
        return self._update_bugs(ids=[id],updates=updates)

    # Eventually - when RHBugzilla is well and truly obsolete - we'll delete
    # all of these methods and refactor the Base Bugzilla object so all the bug
    # modification calls go through _update_bug.
    # Until then, all of these methods are basically just wrappers around it.

    # TODO: allow multiple bug IDs

    def _setstatus(self,id,status,comment='',private=False,private_in_it=False,nomail=False):
        '''Set the status of the bug with the given ID.'''
        update={'bug_status':status}
        if comment:
            update['comment'] = comment
            update['commentprivacy'] = private
        return self._update_bug(id,update)

    def _closebug(self,id,resolution,dupeid,fixedin,comment,isprivate,private_in_it,nomail):
        '''Close the given bug. This is the raw call, and no data checking is
        done here. That's up to the closebug method.
        Note that the private_in_it and nomail args are ignored.'''
        update={'bug_status':'CLOSED','resolution':resolution}
        if dupeid:
            update['resolution'] = 'DUPLICATE'
            update['dupe_id'] = dupeid
        if fixedin:
            update['fixed_in'] = fixedin
        if comment:
            update['comment'] = comment
            if isprivate:
                update['commentprivacy'] = True
        return self._update_bug(id,update)

    def _setassignee(self,id,**data):
        '''Raw xmlrpc call to set one of the assignee fields on a bug.
        changeAssignment($id, $data, $username, $password)
        data: 'assigned_to','reporter','qa_contact','comment'
        returns: [$id, $mailresults]'''
        # drop empty items
        update = dict([(k,v) for k,v in data.iteritems() if (v and v != '')])
        return self._update_bug(id,update)

    def _updatedeps(self,id,blocked,dependson,action):
        '''Update the deps (blocked/dependson) for the given bug.
        blocked, dependson: list of bug ids/aliases
        action: 'add' or 'delete'
        '''
        if action not in ('add','delete'):
            raise ValueError, "action must be 'add' or 'delete'"
        update={'%s_blocked' % action: blocked,
                '%s_dependson' % action: dependson}
        self._update_bug(id,update)

    def _updatecc(self,id,cclist,action,comment='',nomail=False):
        '''Updates the CC list using the action and account list specified.
        cclist must be a list (not a tuple!) of addresses.
        action may be 'add', 'delete', or 'overwrite'.
        comment specifies an optional comment to add to the bug.
        if mail is True, email will be generated for this change.
        '''
        update = {}
        if comment:
            update['comment'] = comment

        if action in ('add','delete'):
            update['%s_cc' % action] = cclist
            self._update_bug(id,update)
        elif action == 'overwrite':
            r = self._getbug(id)
            if 'cc' not in r:
                raise AttributeError, "Can't find cc list in bug %s" % str(id)
            self._updatecc(id,r['cc'],'delete')
            self._updatecc(id,cclist,'add')
        # XXX we don't check inputs on other backend methods, maybe this
        # is more appropriate in the public method(s)
        else:
            raise ValueError, "action must be 'add','delete', or 'overwrite'"

    def _updatewhiteboard(self,id,text,which,action,comment,private):
        '''Update the whiteboard given by 'which' for the given bug.
        performs the given action (which may be 'append',' prepend', or
        'overwrite') using the given text.

        RHBZ3 Bug.update() only supports overwriting, so append/prepend
        may cause two server roundtrips - one to fetch, and one to update.
        '''
        if not which.endswith('_whiteboard'):
            which = which + '_whiteboard'
        update = {}
        if action == 'overwrite':
            update[which] = text
        else:
            r = self._getbug(id)
            if which not in r:
                raise ValueError, "No such whiteboard %s in bug %s" % \
                                   (which,str(id))
            wb = r[which]
            if action == 'prepend':
                update[which] = text+' '+wb
            elif action == 'append':
                update[which] = wb+' '+text
        if comment is not None:
            update['comment'] = comment
            if private:
                update['commentprivacy'] = True
        self._update_bug(id,update)
