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

    def __init__(self, *args, **kwargs):
        """
        @rhbz_back_compat: If True, convert parameters to the format they were
            in prior RHBZ upgrade in June 2012. Mostly this replaces lists
            with comma separated strings, and alters groups and flags.
            Default is False. Please don't use this in new code, just update
            your scripts.
        @multicall: Unused nowadays, will be removed in the future
        """
        # 'multicall' is no longer used, just ignore it
        multicall = kwargs.pop("multicall", None)
        self.rhbz_back_compat = bool(kwargs.pop("rhbz_back_compat", False))

        if multicall is not None:
            log.warn("multicall is unused and will be removed in a "
                "future release.")

        if self.rhbz_back_compat:
            log.warn("rhbz_back_compat will be removed in a future release.")

        _parent.__init__(self, *args, **kwargs)

        def _add_both_alias(newname, origname):
            self._add_field_alias(newname, origname, is_api=False)
            self._add_field_alias(origname, newname, is_bug=False)

        _add_both_alias('fixed_in', 'cf_fixed_in')
        _add_both_alias('qa_whiteboard', 'cf_qa_whiteboard')
        _add_both_alias('devel_whiteboard', 'cf_devel_whiteboard')
        _add_both_alias('internal_whiteboard', 'cf_internal_whiteboard')

        self._add_field_alias('component', 'components', is_bug=False)
        self._add_field_alias('version', 'versions', is_bug=False)
        self._add_field_alias('sub_component', 'sub_components', is_bug=False)

        # flags format isn't exactly the same but it's the closest approx
        self._add_field_alias('flags', 'flag_types')

        self._getbug_extra_fields = self._getbug_extra_fields + [
            "comments", "description",
            "external_bugs", "flags", "sub_components",
            "tags",
        ]
        self._supports_getbug_extra_fields = True


    ######################
    # Bug update methods #
    ######################

    def build_update(self, **kwargs):
        adddict = {}

        def pop(key, destkey):
            val = kwargs.pop(key, None)
            if val is None:
                return
            adddict[destkey] = val

        def get_sub_component():
            val = kwargs.pop("sub_component", None)
            if val is None:
                return

            if type(val) is not dict:
                component = self._listify(kwargs.get("component"))
                if not component:
                    raise ValueError("component must be specified if "
                        "specifying sub_component")
                val = {component[0]: val}
            adddict["sub_components"] = val

        pop("fixed_in", "cf_fixed_in")
        pop("qa_whiteboard", "cf_qa_whiteboard")
        pop("devel_whiteboard", "cf_devel_whiteboard")
        pop("internal_whiteboard", "cf_internal_whiteboard")

        get_sub_component()

        vals = _parent.build_update(self, **kwargs)
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

        # We need to do this for users here for users that
        # don't call build_query
        self._convert_include_field_list(query['include_fields'])

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
        if 'component' in bug and "components" not in bug:
            val = bug['component']
            bug['components'] = type(val) is list and val or [val]
            bug['component'] = bug['components'][0]

        if 'version' in bug and "versions" not in bug:
            val = bug['version']
            bug['versions'] = type(val) is list and val or [val]
            bug['version'] = bug['versions'][0]

        # sub_components isn't too friendly of a format, add a simpler
        # sub_component value
        if 'sub_components' in bug and 'sub_component' not in bug:
            val = bug['sub_components']
            bug['sub_component'] = ""
            if type(val) is dict:
                values = []
                for vallist in val.values():
                    values += vallist
                bug['sub_component'] = " ".join(values)

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

        def _add_key(paramname, keyname, listify=False):
            val = kwargs.pop(paramname, None)
            if val is None:
                return
            if listify:
                val = self._listify(val)
            query[keyname] = val

        def add_longdesc():
            val = kwargs.pop("long_desc", None)
            if val is None:
                return

            query["query_format"] = "advanced"
            query["longdesc"] = val
            query["longdesc_type"] = "allwordssubstr"

        def add_email(key, count):
            value = kwargs.pop(key, None)
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
            value = self._listify(kwargs.pop(kwkey, None))
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

        add_longdesc()

        _add_key("quicksearch", "quicksearch")
        _add_key("savedsearch", "savedsearch")
        _add_key("savedsearch_sharer_id", "sharer_id")
        _add_key("sub_component", "sub_components", listify=True)

        extra_fields = self._convert_include_field_list(
            kwargs.pop('extra_fields', None))
        if extra_fields:
            query["extra_fields"] = extra_fields

        newquery = _parent.build_query(self, **kwargs)
        query.update(newquery)
        self.pre_translation(query)
        return query


# Just for API back compat
class RHBugzilla3(RHBugzilla):
    pass


class RHBugzilla4(RHBugzilla):
    pass
