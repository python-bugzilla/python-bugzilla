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

class Bugzilla3(bugzilla.base.BugzillaBase):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 3.0.x releases.'''

    version = '0.1'
    user_agent = bugzilla.base.user_agent + ' Bugzilla3/%s' % version

    def __init__(self,**kwargs):
        bugzilla.base.BugzillaBase.__init__(self,**kwargs)
        self.user_agent = self.__class__.user_agent

    def _login(self,user,password):
        '''Backend login method for Bugzilla3'''
        return self._proxy.User.login({'login':user,'password':password})

    def _logout(self):
        '''Backend login method for Bugzilla3'''
        return self._proxy.User.logout()

    #---- Methods and properties with basic bugzilla info 

    def _getuserforid(self,userid):
        '''Get the username for the given userid'''
        # STUB FIXME
        return str(userid)

    # Connect the backend methods to the XMLRPC methods
    def _getbugfields(self):
        '''Get a list of valid fields for bugs.'''
        # XXX BZ3 doesn't currently provide anything like the getbugfields()
        # method, so we fake it by looking at bug #1. Yuck.
        keylist = self._getbug(1).keys()
        if 'assigned_to' not in keylist:
            keylist.append('assigned_to')
        return keylist
    def _getqueryinfo(self):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _getproducts(self):
        '''This throws away a bunch of data that RH's getProdInfo
        didn't return. Ah, abstraction.'''
        product_ids = self._proxy.Product.get_accessible_products()
        r = self._proxy.Product.get_products(product_ids)
        return r['products']
    def _getcomponents(self,product):
        if type(product) == str:
            product = self._product_name_to_id(product)
        r = self._proxy.Bug.legal_values({'product_id':product,'field':'component'})
        return r['values']
    def _getcomponentsdetails(self,product):
        raise NotImplementedError

    #---- Methods for reading bugs and bug info

    def _getbugs(self,idlist):
        '''Return a list of dicts of full bug info for each given bug id'''
        r = self._proxy.Bug.get_bugs({'ids':idlist})
        return [i['internals'] for i in r['bugs']]
    def _getbug(self,id):
        '''Return a dict of full bug info for the given bug id'''
        return self._getbugs([id])[0]
   # Bugzilla3 doesn't have getbugsimple - alias to the full method(s)
    _getbugsimple = _getbug
    _getbugssimple = _getbugs

    # Bugzilla 3.0 doesn't have a *lot* of things, actually. 
    def _query(self,query):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _addcomment(self,id,comment,private=False,
                   timestamp='',worktime='',bz_gid=''):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _setstatus(self,id,status,comment='',private=False,private_in_it=False,nomail=False):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _closebug(self,id,resolution,dupeid,fixedin,comment,isprivate,private_in_it,nomail):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _setassignee(self,id,**data):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _updatedeps(self,id,deplist):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _updatecc(self,id,cclist,action,comment='',nomail=False):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _updatewhiteboard(self,id,text,which,action):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    # TODO: update this when the XMLRPC interface grows requestee support
    def _updateflags(self,id,flags):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."
    def _attachfile(self,id,**attachdata):
        raise NotImplementedError, "Bugzilla 3.0 does not support this method."

    #---- createbug - call to create a new bug

    createbug_required = ('product','component','summary','version',
                          'op_sys','platform')
    def _createbug(self,**data):
        '''Raw xmlrpc call for createBug() Doesn't bother guessing defaults
        or checking argument validity. Use with care.
        Returns bug_id'''
        r = self._proxy.Bug.create(data)
        return r['id']

# Bugzilla 3.2 adds some new goodies on top of Bugzilla3.
class Bugzilla32(Bugzilla3):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 3.2.x releases.
    
    For further information on the methods defined here, see the API docs:
    http://www.bugzilla.org/docs/3.2/en/html/api/
    '''

    version = '0.1'
    user_agent = bugzilla.base.user_agent + ' Bugzilla32/%s' % version

    def _addcomment(self,id,comment,private=False,
                   timestamp='',worktime='',bz_gid=''):
        '''Add a comment to the bug with the given ID. Other optional 
        arguments are as follows:
            private:   if True, mark this comment as private.
            timestamp: comment timestamp, in the form "YYYY-MM-DD HH:MM:SS"
                       Ignored by BZ32.
            worktime:  amount of time spent on this comment, in hours
            bz_gid:    if present, and the entire bug is *not* already private
                       to this group ID, this comment will be marked private.
        '''
        return self._proxy.Bug.add_comment({'id':id,
                                            'comment':comment,
                                            'private':private,
                                            'work_time':worktime})

class RHBugzilla32(Bugzilla32):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by Red Hat's Bugzilla 3.1.4+ instance, which are supposed
    to make their way into Bugzilla 3.4.
    
    This class was written using bugzilla.redhat.com's API docs:
    https://bugzilla.redhat.com/docs/en/html/api/
    '''

    version = '0.1'
    user_agent = bugzilla.base.user_agent + ' RHBugzilla32/%s' % version

    def _query(self,query):
        '''Query bugzilla and return a list of matching bugs.
        query must be a dict with fields like those in in querydata['fields'].
        You can also pass in keys called 'quicksearch' or 'savedsearch' - 
        'quicksearch' will do a quick keyword search like the simple search
        on the Bugzilla home page. 
        'savedsearch' should be the name of a previously-saved search to
        execute. You need to be logged in for this to work.
        Returns a dict like this: {'bugs':buglist,
                                   'sql':querystring}
        buglist is a list of dicts describing bugs, and 'sql' contains the SQL
        generated by executing the search.
        ''' 
        # The following is true for rhbz; not sure if it's the case for BZ3.2
        #You can specify which columns/keys will be listed in the bugs by 
        #setting 'column_list' in the query; otherwise the default columns are 
        #used (see the list in querydefaults['default_column_list']). 
        return self._proxy.Bug.search(query)

    #---- Methods for updating bugs.

    def _update_bug(self,id,updates):
        '''Update a single bug, specified by integer ID or (string) bug alias.
        Really just a convenience method for _update_bugs(ids=[id],updates)'''
        return self._update_bugs(ids=[id],updates=updates)

    def _update_bugs(self,ids,updates):
        '''Update the given fields with the given data in one or more bugs.
        ids should be a list of integers or strings, representing bug ids or
        aliases.
        updates is a dict containing pairs like so: {'fieldname':'newvalue'}
        '''
        # TODO document changeable fields & return values
        # TODO I think we need to catch XMLRPC exceptions to get 
        return self._proxy.Bug.update({'ids':ids,'updates':updates})

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
        update = dict([(k,v) for k,v in data.iteritems() if v != ''])
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
        action may be 'add', 'remove', or 'makeexact'.
        comment specifies an optional comment to add to the bug.
        if mail is True, email will be generated for this change.
        '''
        raise NotImplementedError, "wwoods needs to port this method."

    def _updatewhiteboard(self,id,text,which,action):
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
                raise ValueError, "No such whiteboard %s in bug %i" % (which,id)
            wb = r[which]
            if action == 'prepend':
                update[which] = text+' '+wb
            elif action == 'append':
                update[which] = wb+' '+text
        self._update_bug(id,update)

    # TODO: update this when the XMLRPC interface grows requestee support
    def _updateflags(self,id,flags):
        '''Updates the flags associated with a bug report.
        data should be a hash of {'flagname':'value'} pairs, like so:
        {'needinfo':'?','fedora-cvs':'+'}
        You may also add a "nomail":1 item, which will suppress email if set.

        NOTE: the Red Hat XMLRPC interface does not yet support setting the
        requestee (as in: needinfo from smartguy@answers.com). Alas.'''
        raise NotImplementedError, "wwoods needs to port this method."

    #---- Methods for working with attachments

    # If your bugzilla wants attachments in something other than base64, you
    # should override _attachment_encode here.
    # If your bugzilla uses non-standard paths for attachment.cgi, you'll 
    # want to override _attachment_uri here.

    def _attachfile(self,id,**attachdata):
        raise NotImplementedError, "wwoods needs to port this method."

