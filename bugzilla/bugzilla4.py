# bugzilla4.py - a really simple Python interface to Bugzilla 4.x using xmlrpclib.
#
# Copyright (C) 2008-2012 Red Hat Inc.
# Author: Michal Novotny <minovotn@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import bugzilla.base
from bugzilla.bugzilla3 import Bugzilla36

class Bugzilla4(Bugzilla36):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 4.0.x releases.'''

    version = '0.1'
    user_agent = bugzilla.base.user_agent + ' Bugzilla4/%s' % version
    #createbug_required = ('product','component','summary','version')

    createbug_required = ('product','component','summary','version',
                          'op_sys','platform')

    def __init__(self,**kwargs):
        Bugzilla36.__init__(self, **kwargs)
        self.user_agent = self.__class__.user_agent

    field_aliases = (Bugzilla36.field_aliases +
                     (("creator", "reporter"),))
    #---- Methods for reading bugs and bug info

    def _getbugs(self,idlist):
        '''Return a list of dicts of full bug info for each given bug id.
        bug ids that couldn't be found will return None instead of a dict.'''
        # XXX This is only slightly different from Bugzilla36, combine them?
        idlist = map(lambda i: int(i), idlist)
        r = self._proxy.Bug.get_bugs({'ids':idlist, 'permissive': 1})
        bugdict = dict([(b['id'], b) for b in r['bugs']])
        return [bugdict.get(i) for i in idlist]
    def _getbug(self,id):
        '''Return a dict of full bug info for the given bug id'''
        return self._getbugs([id])[0]

   # TODO: Bugzilla4 should support getbugsimple, needs to be implemented
    _getbugsimple = _getbug
    _getbugssimple = _getbugs

    def build_query(self, **kwargs):
        query = Bugzilla36.build_query(self, **kwargs)

        # 'include_fields' only available for Bugzilla4+
        include_fields = kwargs.get('include_fields', None)
        if not include_fields is None:
            query["include_fields"] = include_fields

            # Translate old style fields
            for newname, oldname in self.field_aliases:
                if oldname in include_fields:
                    include_fields.remove(oldname)
                    if newname not in include_fields:
                        include_fields.append(newname)

            # We always need the id
            if 'id' not in include_fields:
                include_fields.append('id')

        return query
