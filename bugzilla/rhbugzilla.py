# rhbugzilla.py - a Python interface to Red Hat Bugzilla using xmlrpclib.
#
# Copyright (C) 2008-2012 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.


from bugzilla import log
from bugzilla.bugzilla4 import Bugzilla42


class RHBugzilla(Bugzilla42):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by Red Hat's Bugzilla 4.2+ instance, which is a superset
    of the Bugzilla 4.2 methods. The additional methods (e.g. Bug.update)
    should make their way into a later upstream Bugzilla release.

    Note that RHBZ4 *also* supports most of the old RHBZ methods, under the
    'bugzilla' namespace, so we use those when BZ4 methods aren't available.

    This class was written using bugzilla.redhat.com's API docs:
    https://bugzilla.redhat.com/docs/en/html/api/

    By default, _getbugs will multicall getBug(id) multiple times, rather than
    doing a single Bug.get(idlist) call. You can disable this behavior by
    setting the 'multicall' property to False. This will make it somewhat
    faster, but any missing/unreadable bugs will cause the entire call to
    Fault rather than returning any data.
    '''

    version = '0.1'

    def __init__(self, **kwargs):
        # 'multicall' is no longer used, keep it here for back compat
        self.multicall = True
        if "multicall" in kwargs:
            self.multicall = kwargs.pop("multicall")

        Bugzilla42.__init__(self, **kwargs)

    getbug_extra_fields = (
        Bugzilla42.getbug_extra_fields + [
            "attachments", "comments", "description",
            "external_bugs", "flags",
        ]
    )

    field_aliases = (
        Bugzilla42.field_aliases + (
            ('fixed_in', 'cf_fixed_in'),
            ('qa_whiteboard', 'cf_qa_whiteboard'),
            ('devel_whiteboard', 'cf_devel_whiteboard'),
            ('internal_whiteboard', 'cf_internal_whiteboard'),
        )
    )


    ################
    # User methods #
    ################

    def _updateperms(self, user, action, groups):
        r = self._proxy.bugzilla.updatePerms(user, action, groups, self.user,
                self.password)
        return r

    def _adduser(self, user, name):
        r = self._proxy.bugzilla.addUser(user, name, self.user, self.password)
        return r


    #####################
    # Component methods #
    #####################

    def _addcomponent(self, data):
        add_required_fields = ('product', 'component',
                               'initialowner', 'description')
        for field in add_required_fields:
            if field not in data or not data[field]:
                raise TypeError("mandatory fields missing: %s" % field)
        if type(data['product']) == int:
            data['product'] = self._product_id_to_name(data['product'])
        r = self._proxy.bugzilla.addComponent(data, self.user, self.password)
        return r

    def _editcomponent(self, data):
        edit_required_fields = ('initialowner', 'product', 'component')
        for field in edit_required_fields:
            if field not in data or not data[field]:
                raise TypeError("mandatory field missing: %s" % field)
        if type(data['product']) == int:
            data['product'] = self._product_id_to_name(data['product'])
        r = self._proxy.bugzilla.editComponent(data, self.user, self.password)
        return r


    ######################
    # Bug update methods #
    ######################

    def build_update(self, *args, **kwargs):
        adddict = {}

        def pop(key, destkey):
            if key not in kwargs:
                return

            val = kwargs.pop(key)
            if val is None:
                return
            adddict[destkey] = val

        pop("fixed_in", "cf_fixed_in")
        pop("qa_whiteboard", "cf_qa_whiteboard")
        pop("devel_whiteboard", "cf_devel_whiteboard")
        pop("internal_whiteboard", "cf_internal_whiteboard")

        vals = Bugzilla42.build_update(self, *args, **kwargs)
        vals.update(adddict)

        return vals


    #################
    # Query methods #
    #################

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

        if 'include_fields' not in query and 'column_list' not in query:
            return

        if 'include_fields' not in query:
            query['include_fields'] = list()
            if 'column_list' in query:
                query['include_fields'] = query['column_list']
                del query['column_list']

        include_fields = query['include_fields']
        for newname, oldname in self.field_aliases:
            if oldname in include_fields:
                include_fields.remove(oldname)
                if newname not in include_fields:
                    include_fields.append(newname)

    def post_translation(self, query, bug):
        '''Translates the query result'''
        tmpstr = []
        if 'flags' in bug:
            for tmp in bug['flags']:
                tmpstr.append("%s%s" % (tmp['name'], tmp['status']))

            bug['flags'] = ",".join(tmpstr)
        if 'blocks' in bug:
            if len(bug['blocks']) > 0:
                bug['blockedby'] = ','.join([str(b) for b in bug['blocks']])
                bug['blocked'] = ','.join([str(b) for b in bug['blocks']])
            else:
                bug['blockedby'] = ''
                bug['blocked'] = ''
        if 'keywords' in bug:
            if len(bug['keywords']) > 0:
                bug['keywords'] = ','.join(bug['keywords'])
            else:
                bug['keywords'] = ''
        if 'component' in bug:
            # we have to emulate the old behavior and add 'components' as
            # list instead
            bug['components'] = bug['component']
            bug['component'] = bug['component'][0]
        if 'alias' in bug:
            if len(bug['alias']) > 0:
                bug['alias'] = ','.join(bug['alias'])
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

    def build_query(self, **kwargs):
        query = {}

        def add_email(key, count):
            if not key in kwargs:
                return count

            value = kwargs.get(key)
            del(kwargs[key])
            if value is None:
                return count

            query["query_format"] = "advanced"
            query['email%i' % count] = value
            query['email%s%i' % (key, count)] = True
            query['emailtype%i' % count] = kwargs.get("emailtype", "substring")
            return count + 1

        def bool_smart_split(boolval):
            # This parses the CLI command syntax, but we only want to
            # do space splitting if the space is actually part of a
            # boolean operator
            boolchars = ["|", "&", "!"]
            add = ""
            retlist = []

            for word in boolval.split(" "):
                if word.strip() in boolchars:
                    word = word.strip()
                    if add:
                        retlist.append(add)
                        add = ""
                    retlist.append(word)
                else:
                    if add:
                        add += " "
                    add += word

            if add:
                retlist.append(add)
            return retlist

        def add_boolean(kwkey, key, bool_id):
            if not kwkey in kwargs:
                return bool_id

            value = kwargs.get(kwkey)
            del(kwargs[kwkey])
            if value is None:
                return bool_id

            query["query_format"] = "advanced"
            for boolval in value:
                and_count = 0
                or_count = 0

                def make_bool_str(prefix):
                    return "%s%i-%i-%i" % (prefix, bool_id,
                                           and_count, or_count)

                for par in bool_smart_split(boolval):
                    field = None
                    fval = par
                    typ = kwargs.get("booleantype", "substring")

                    if par == "&":
                        and_count += 1
                    elif par == "|":
                        or_count += 1
                    elif par == "!":
                        query['negate%i' % bool_id] = 1
                    elif not key:
                        if par.find('-') == -1:
                            raise RuntimeError('Malformed boolean query: %s' %
                                               value)

                        args = par.split('-', 2)
                        field = args[0]
                        typ = args[1]
                        fval = None
                        if len(args) == 3:
                            fval = args[2]
                    else:
                        field = key

                    query[make_bool_str("field")] = field
                    if fval:
                        query[make_bool_str("value")] = fval
                    query[make_bool_str("type")] = typ

                bool_id += 1
            return bool_id

        # Use fancy email specification for RH bugzilla. It isn't
        # strictly required, but is more powerful, and it is what
        # bin/bugzilla historically generated. This requires
        # query_format='advanced' which is an RHBZ only XMLRPC extension
        email_count = 1
        email_count = add_email("cc", email_count)
        email_count = add_email("assigned_to", email_count)
        email_count = add_email("reporter", email_count)
        email_count = add_email("qa_contact", email_count)

        chart_id = 0
        chart_id = add_boolean("fixed_in", "cf_fixed_in", chart_id)
        chart_id = add_boolean("blocked", "blocked", chart_id)
        chart_id = add_boolean("dependson", "dependson", chart_id)
        chart_id = add_boolean("flag", "flagtypes.name", chart_id)
        chart_id = add_boolean("qa_whiteboard", "cf_qa_whiteboard", chart_id)
        chart_id = add_boolean("devel_whiteboard", "cf_devel_whiteboard",
                               chart_id)
        chart_id = add_boolean("alias", "alias", chart_id)
        chart_id = add_boolean("boolean_query", None, chart_id)

        newquery = Bugzilla42.build_query(self, **kwargs)
        query.update(newquery)
        self.pre_translation(query)
        return query

    def _query(self, query):
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
        http://www.bugzilla.org/docs/4.0/en/html/api/Bugzilla/
        '''
        old = query.copy()
        self.pre_translation(query)

        if old != query:
            log.debug("RHBugzilla altered query to: %s", query)

        ret = self._proxy.Bug.search(query)

        # Unfortunately we need a hack to preserve backwards
        # compabibility with older RHBZ
        for bug in ret['bugs']:
            self.post_translation(query, bug)

        return ret


# Just for API back compat
class RHBugzilla3(RHBugzilla):
    pass


class RHBugzilla4(RHBugzilla):
    pass
