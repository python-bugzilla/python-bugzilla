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
from bugzilla.bugzilla4 import Bugzilla44 as _parent


class RHBugzilla(_parent):
    '''
    Bugzilla class for connecting Red Hat's forked bugzilla instance,
    bugzilla.redhat.com

    Historically this class used many more non-upstream methods, but
    in 2012 RH started dropping most of its custom bits. By that time,
    upstream BZ had most of the important functionality.

    Much of the remaining code here is just trying to keep things operating
    in python-bugzilla back compatible manner.

    This class was written using bugzilla.redhat.com's API docs:
    https://bugzilla.redhat.com/docs/en/html/api/
    '''

    version = '0.1'

    def __init__(self, **kwargs):
        """
        @multicall: No longer used
        @rhbz_back_compat: If True, convert parameters to the format they were
                           in prior RHBZ upgrade in June 2012. Mostly this
                           replaces lists with comma separated strings,
                           and alters groups and flags. Default is False
        """
        # 'multicall' is no longer used, keep it here for back compat
        self.multicall = True
        self.rhbz_back_compat = False

        if "multicall" in kwargs:
            self.multicall = kwargs.pop("multicall")
        if "rhbz_back_compat" in kwargs:
            self.rhbz_back_compat = bool(kwargs.pop("rhbz_back_compat"))

        _parent.__init__(self, **kwargs)

    getbug_extra_fields = (
        _parent.getbug_extra_fields + [
            "attachments", "comments", "description",
            "external_bugs", "flags",
        ]
    )

    field_aliases = (
        _parent.field_aliases + (
            ('fixed_in', 'cf_fixed_in'),
            ('qa_whiteboard', 'cf_qa_whiteboard'),
            ('devel_whiteboard', 'cf_devel_whiteboard'),
            ('internal_whiteboard', 'cf_internal_whiteboard'),
            # Format isn't exactly the same but it's the closest approximation
            ('flags', 'flag_types'),
        )
    )


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

        vals = _parent.build_update(self, *args, **kwargs)
        vals.update(adddict)

        return vals


    #################
    # Query methods #
    #################

    def pre_translation(self, query):
        '''Translates the query for possible aliases'''
        old = query.copy()

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
            query['include_fields'] = []
            if 'column_list' in query:
                query['include_fields'] = query['column_list']
                del query['column_list']

        include_fields = query['include_fields']
        for newname, oldname in self.field_aliases:
            if oldname in include_fields:
                include_fields.remove(oldname)
                if newname not in include_fields:
                    include_fields.append(newname)

        if old != query:
            log.debug("RHBugzilla pretranslated query to: %s", query)

    def post_translation(self, query, bug):
        '''
        Convert the results of getbug back to the ancient RHBZ value
        formats
        '''
        ignore = query

        # RHBZ _still_ returns component and version as lists, which
        # deviates from upstream. Copy the list values to components
        # and versions respectively.
        if 'component' in bug and not "components" in bug:
            val = bug['component']
            bug['components'] = type(val) is list and val or [val]
            bug['component'] = bug['components'][0]

        if 'version' in bug and not "versions" in bug:
            val = bug['version']
            bug['versions'] = type(val) is list and val or [val]
            bug['version'] = bug['versions'][0]

        if not self.rhbz_back_compat:
            return

        if 'flags' in bug and type(bug["flags"]) is list:
            tmpstr = []
            for tmp in bug['flags']:
                tmpstr.append("%s%s" % (tmp['name'], tmp['status']))

            bug['flags'] = ",".join(tmpstr)

        if 'blocks' in bug and type(bug["blocks"]) is list:
            # Aliases will handle the 'blockedby' and 'blocked' back compat
            bug['blocks'] = ','.join([str(b) for b in bug['blocks']])

        if 'keywords' in bug and type(bug["keywords"]) is list:
            bug['keywords'] = ','.join(bug['keywords'])

        if 'alias' in bug and type(bug["alias"]) is list:
            bug['alias'] = ','.join(bug['alias'])

        if ('groups' in bug and
            type(bug["groups"]) is list and
            len(bug["groups"]) > 0 and
            type(bug["groups"][0]) is str):
            # groups went to the opposite direction: it got simpler
            # instead of having name, ison, description, it's now just
            # an array of strings of the groups the bug belongs to
            # we're emulating the old behaviour here
            tmp = []
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

            value = self._listify(kwargs.pop(kwkey))
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

        newquery = _parent.build_query(self, **kwargs)
        query.update(newquery)
        self.pre_translation(query)
        return query


# Just for API back compat
class RHBugzilla3(RHBugzilla):
    pass


class RHBugzilla4(RHBugzilla):
    pass
