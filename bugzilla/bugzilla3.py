# bugzilla3.py - a Python interface to Bugzilla 3.x using xmlrpclib.
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

version = '0.1'
user_agent = bugzilla.base.user_agent + ' Bugzilla3/%s' % version

class Bugzilla3(bugzilla.base.BugzillaBase):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 3.x releases.'''
    def __init__(self,**kwargs):
        bugzilla.base.BugzillaBase.__init__(self,**kwargs)
        self.user_agent = user_agent

    def _login(self,user,password):
        '''Backend login method for Bugzilla3'''
        return self._proxy.User.login({'login':user,'password':password})

    #---- Methods and properties with basic bugzilla info 

    def _getuserforid(self,userid):
        '''Get the username for the given userid'''
        # STUB FIXME
        return str(userid)

    # Connect the backend methods to the XMLRPC methods
    def _getbugfields(self):
        '''Get a list of valid fields for bugs.'''
        #I don't think BZ3 provides a getbugfields() method, so right 
        #we fake it by looking at bug #1. Yuck.
        keylist = self._getbug(1).keys()
        if 'assigned_to' not in keylist:
            keylist.append('assigned_to')
        return keylist
    def _getqueryinfo(self):
        #return self._proxy.bugzilla.getQueryInfo(self.user,self.password)
        raise NotImplementedError
    def _getproducts(self):
        '''This throws away a bunch of data that RH's getProdInfo
        didn't return. Ah, abstraction.'''
        product_ids = self._proxy.Product.get_accessible_products()
        r = self._proxy.Product.get_products(product_ids)
        pdict = {}
        for p in r['products']:
            pdict[p['name']] = p['description']
        return pdict

    def _getcomponents(self,product):
        #return self._proxy.bugzilla.getProdCompInfo(product,self.user,self.password)
        raise NotImplementedError
    def _getcomponentsdetails(self,product):
        #return self._proxy.bugzilla.getProdCompDetails(product,self.user,self.password)
        raise NotImplementedError

    #---- Methods for reading bugs and bug info

    def _getbugs(self,idlist):
        r = self._proxy.Bug.get_bugs({'ids':idlist})
        return [i['internals'] for i in r['bugs']]
    def _getbug(self,id):
        '''Return a dict of full bug info for the given bug id'''
        return self._getbugs([id])[0]
    def _getbugsimple(self,id):
        '''Return a short dict of simple bug info for the given bug id'''
        # Bugzilla3 doesn't have this
        return self._getbug(id)

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
        #return self._proxy.bugzilla.runQuery(query,self.user,self.password)
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."

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
    def _setassignee(self,id,**data):
        '''Raw xmlrpc call to set one of the assignee fields on a bug.
        changeAssignment($id, $data, $username, $password)
        data: 'assigned_to','reporter','qa_contact','comment'
        returns: [$id, $mailresults]'''
        return self._proxy.bugzilla.changeAssignment(id,data,self.user,self.password)
    def _updatedeps(self,id,deplist):
        '''IMPLEMENT ME: update the deps (blocked/dependson) for the given bug.
        updateDepends($bug_id,$data,$username,$password,$nodependencyemail)
        #data: 'blocked'=>id,'dependson'=>id,'action' => ('add','remove')'''
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

    # If your bugzilla wants attachments in something other than base64, you
    # should override _attachment_encode here.
    # If your bugzilla uses non-standard paths for attachment.cgi, you'll 
    # want to override _attachment_uri here.

    def _attachfile(self,id,**attachdata):
        return self._proxy.bugzilla.addAttachment(id,attachdata,self.user,self.password)

    #---- createbug - call to create a new bug

    createbug_required = ('product','component','summary','version',
                          'op_sys','platform')

    def _createbug(self,**data):
        '''Raw xmlrpc call for createBug() Doesn't bother guessing defaults
        or checking argument validity. Use with care.
        Returns bug_id'''
        r = self._proxy.Bug.create(data)
        return r['id']
