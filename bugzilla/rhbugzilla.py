# rhbugzilla.py - a Python interface to Red Hat Bugzilla using xmlrpclib.
#
# Copyright (C) 2008 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import bugzilla.base

version = '0.2'
user_agent = bugzilla.base.user_agent + ' RHBugzilla/%s' % version

class RHBugzilla(bugzilla.base.BugzillaBase):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by Red Hat's Bugzilla 2.18 variant.'''
    def __init__(self,**kwargs):
        bugzilla.base.BugzillaBase.__init__(self,**kwargs)
        self.user_agent = user_agent

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
        return replace_getbug_errors_with_None(raw_results)
    def _getbugssimple(self,idlist):
        '''Like _getbugsimple, but takes a list of ids and returns a
        corresponding list of bug objects. Uses multicall for awesome speed.'''
        mc = self._multicall()
        for id in idlist:
            mc._getbugsimple(id)
        raw_results = mc.run()
        del mc
        # check results for xmlrpc errors, and replace them with None
        return replace_getbug_errors_with_None(raw_results)

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
    def _updatewhiteboard(self,id,text,which,action):
        '''Update the whiteboard given by 'which' for the given bug.
        performs the given action (which may be 'append',' prepend', or 
        'overwrite') using the given text.'''
        data = {'type':which,'text':text,'action':action}
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
