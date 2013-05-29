# bugzilla3.py - a Python interface to Bugzilla 3.x using xmlrpclib.
#
# Copyright (C) 2008, 2009 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from bugzilla.base import BugzillaBase


class Bugzilla3(BugzillaBase):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 3.0.x releases.'''

    version = '0.1'
    bz_ver_major = 3
    bz_ver_minor = 0

    def __init__(self, **kwargs):
        BugzillaBase.__init__(self, **kwargs)


    # Connect the backend methods to the XMLRPC methods
    def _getbugfields(self):
        '''Get a list of valid fields for bugs.'''
        # BZ3 doesn't currently provide anything like the getbugfields()
        # method, so we fake it by looking at bug #1. Yuck.
        # And at least gnome.bugzilla.org fails to lookup bug #1, so
        # try a few
        err = False
        for bugid in [1, 100000]:
            try:
                keylist = self._getbug(bugid).keys()
                err = False
                break
            except Exception:
                err = True

        if err:
            raise

        return keylist


# Bugzilla 3.2 adds some new goodies on top of Bugzilla3.
class Bugzilla32(Bugzilla3):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 3.2.x releases.

    For further information on the methods defined here, see the API docs:
    http://www.bugzilla.org/docs/3.2/en/html/api/
    '''
    version = '0.1'
    bz_ver_minor = 2


# Bugzilla 3.4 adds some new goodies on top of Bugzilla32.
class Bugzilla34(Bugzilla32):
    version = '0.2'
    bz_ver_minor = 4


class Bugzilla36(Bugzilla34):
    version = '0.1'
    bz_ver_minor = 6

    def _getbugfields(self):
        '''Get the list of valid fields for Bug objects'''
        r = self._proxy.Bug.fields({'include_fields': ['name']})
        return [f['name'] for f in r['fields']]
