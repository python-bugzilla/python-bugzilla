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

    def pre_translation(self, query):
        '''Translates the query for possible aliases'''
        if 'bug_id' in query:
            if type(query['bug_id']) is not list:
                query['id'] = query['bug_id'].split(',')
            else:
                query['id'] = query['bug_id']
            del query['bug_id']

        if 'component' in query:
            if type(query['component']) is not list:
                query['component'] = query['component'].split(',')

        if 'include_fields' not in query:
            query['include_fields'] = list()
            if 'column_list' in query:
                query['include_fields'] = query['column_list']
                del query['column_list']

        if 'blockedby' in query['include_fields']:
            query['include_fields'].remove('blockedby')
            query['include_fields'].append('blocks')

        if 'bug_status' in query['include_fields']:
            query['include_fields'].remove('bug_status')
            query['include_fields'].append('status')

        if 'short_desc' in query['include_fields']:
            query['include_fields'].remove('short_desc')
            query['include_fields'].append('summary')

        if 'status_whiteboard' in query['include_fields']:
            query['include_fields'].remove('status_whiteboard')
            query['include_fields'].append('whiteboard')

        if 'bug_id' in query['include_fields']:
            query['include_fields'].remove('bug_id')
            query['include_fields'].append('id')
        elif 'id' not in query['include_fields']:
            # we always need the id
            query['include_fields'].append('id')

    def post_translation(self, query, bug):
        '''Translates the query result'''
        tmpstr = []
        if 'flags' in bug:
            for tmp in bug['flags']:
                tmpstr.append("%s%s" % (tmp['name'], tmp['status']))

            bug['flags'] = ", ".join(tmpstr)
        if 'blocks' in bug:
            if len(bug['blocks']) > 0:
                bug['blockedby'] = ', '.join(map(str, bug['blocks']))
                bug['blocked'] = ', '.join(map(str, bug['blocks']))
            else:
                bug['blockedby'] = ''
                bug['blocked'] = ''
        if 'id' in bug:
            bug['bug_id'] = bug['id']
        if 'keywords' in bug:
            if len(bug['keywords']) > 0:
                bug['keywords'] = ', '.join(bug['keywords'])
            else:
                bug['keywords'] = ''
        if 'component' in bug:
            # we have to emulate the old behavior and add 'components' as
            # list instead
            bug['components'] = bug['component']
            bug['component'] = bug['component'][0]
        if 'alias' in bug:
            if len(bug['alias']) > 0:
                bug['alias'] = ', '.join(bug['alias'])
            else:
                bug['alias'] = ''
        if 'groups' in bug:
            # groups went to the opposite direction: it got simpler
            # instead of having name, ison, description, it's now just
            # an array of strings of the groups the bug belongs to
            # we're emulating the old behaviour here
            tmp = list()
            for g in bug['groups']:
                t = {}
                t['name'] = g
                t['description'] = g
                t['ison'] = 1
                tmp.append(t)
            bug['groups'] = tmp
        if 'summary' in bug:
            bug['short_desc'] = bug['summary']
        if 'whiteboard' in bug:
            bug['status_whiteboard'] = bug['whiteboard']
        if 'status' in bug:
            bug['bug_status'] = bug['status']

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
        You can also pass 'limit:[int]' to limit the number of results.
        For more info, see:
        http://www.bugzilla.org/docs/4.0/en/html/api/Bugzilla/WebService/Bug.html
        '''
        self.pre_translation(query)

        ret = self._proxy.Bug.search(query)

        # Unfortunately we need a hack to preserve backwards compabibility with older BZs
        for bug in ret['bugs']:
            self.post_translation(query, bug)

        return ret

    def _getbugfields(self):
        '''Get the list of valid fields for Bug objects'''
        r = self._proxy.Bug.fields({'include_fields':['name']})
        tmp = [f['name'] for f in r['fields']]
        tmp.append('blockedby')
        tmp.append('components')

        # XXX - bugzilla lists for us "bug_status" which is wrong. making sure
        #       we have the correct list
        if 'bug_status' in tmp:
            tmp.remove('bug_status')
        if 'status' not in tmp:
            tmp.append('status')

        return tmp
        # NOTE: the RHBZ version lists 'comments' and 'groups', and strips
        # the 'cf_' from the beginning of custom fields.
