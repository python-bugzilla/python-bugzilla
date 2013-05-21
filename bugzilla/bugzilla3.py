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


    #---- Methods for reading bugs and bug info

    def _getbugs(self, idlist, simple=False):
        '''
        Return a list of dicts of full bug info for each given bug id.
        bug ids that couldn't be found will return None instead of a dict.

        @simple: If True, don't ask for any large extra_fields.
        '''
        idlist = [int(i) for i in idlist]

        getbugdata = {
            "ids": idlist,
            "permissive": 1,
        }
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
        return self._getbugs([objid], simple=simple)[0]

    # Since for so long getbugsimple == getbug, I don't think we can
    # remove any fields without possibly causing a slowdown for some
    # existing users. Just have this API mean 'don't ask for the extra
    # big stuff'
    def _getbugsimple(self, objid):
        return self._getbug(objid, simple=True)

    def _getbugssimple(self, idlist):
        return self._getbugs(idlist, simple=True)




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


class Bugzilla36(Bugzilla34):
    version = '0.1'
    bz_ver_minor = 6

    def _getbugfields(self):
        '''Get the list of valid fields for Bug objects'''
        r = self._proxy.Bug.fields({'include_fields': ['name']})
        return [f['name'] for f in r['fields']]
