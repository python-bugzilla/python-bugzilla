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
# Well, okay. It adds one new goodie.
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

