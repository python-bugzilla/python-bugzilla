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

from logging import getLogger

from .bugzilla4 import Bugzilla44 as _parent

log = getLogger(__name__)


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

            if not isinstance(val, dict):
                component = self._listify(kwargs.get("component"))
                if not component:
                    raise ValueError("component must be specified if "
                        "specifying sub_component")
                val = {component[0]: val}
            adddict["sub_components"] = val

        def get_alias():
            # RHBZ has a custom extension to allow a bug to have multiple
            # aliases, so the format of aliases is
            #    {"add": [...], "remove": [...]}
            # But that means in order to approximate upstream, behavior
            # which just overwrites the existing alias, we need to read
            # the bug's state first to know what string to remove. Which
            # we can't do, since we don't know the bug numbers at this point.
            # So fail for now.
            #
            # The API should provide {"set": [...]}
            # https://bugzilla.redhat.com/show_bug.cgi?id=1173114
            #
            # Implementation will go here when it's available
            pass

        pop("fixed_in", "cf_fixed_in")
        pop("qa_whiteboard", "cf_qa_whiteboard")
        pop("devel_whiteboard", "cf_devel_whiteboard")
        pop("internal_whiteboard", "cf_internal_whiteboard")

        get_sub_component()
        get_alias()

        vals = _parent.build_update(self, **kwargs)
        vals.update(adddict)

        return vals

    def add_external_tracker(self, bug_ids, ext_bz_bug_id, ext_type_id=None,
                             ext_type_description=None, ext_type_url=None,
                             ext_status=None, ext_description=None,
                             ext_priority=None):
        """
        Wrapper method to allow adding of external tracking bugs using the
        ExternalBugs::WebService::add_external_bug method.

        This is documented at
        https://bugzilla.redhat.com/docs/en/html/api/extensions/ExternalBugs/lib/WebService.html#add_external_bug

        bug_ids: A single bug id or list of bug ids to have external trackers
            added.
        ext_bz_bug_id: The external bug id (ie: the bug number in the
            external tracker).
        ext_type_id: The external tracker id as used by Bugzilla.
        ext_type_description: The external tracker description as used by
            Bugzilla.
        ext_type_url: The external tracker url as used by Bugzilla.
        ext_status: The status of the external bug.
        ext_description: The description of the external bug.
        ext_priority: The priority of the external bug.
        """
        param_dict = {'ext_bz_bug_id': ext_bz_bug_id}
        if ext_type_id is not None:
            param_dict['ext_type_id'] = ext_type_id
        if ext_type_description is not None:
            param_dict['ext_type_description'] = ext_type_description
        if ext_type_url is not None:
            param_dict['ext_type_url'] = ext_type_url
        if ext_status is not None:
            param_dict['ext_status'] = ext_status
        if ext_description is not None:
            param_dict['ext_description'] = ext_description
        if ext_priority is not None:
            param_dict['ext_priority'] = ext_priority
        params = {
            'bug_ids': self._listify(bug_ids),
            'external_bugs': [param_dict],
        }
        return self._proxy.ExternalBugs.add_external_bug(params)

    def update_external_tracker(self, ids=None, ext_type_id=None,
                                ext_type_description=None, ext_type_url=None,
                                ext_bz_bug_id=None, bug_ids=None,
                                ext_status=None, ext_description=None,
                                ext_priority=None):
        """
        Wrapper method to allow adding of external tracking bugs using the
        ExternalBugs::WebService::update_external_bug method.

        This is documented at
        https://bugzilla.redhat.com/docs/en/html/api/extensions/ExternalBugs/lib/WebService.html#update_external_bug

        ids: A single external tracker bug id or list of external tracker bug
            ids.
        ext_type_id: The external tracker id as used by Bugzilla.
        ext_type_description: The external tracker description as used by
            Bugzilla.
        ext_type_url: The external tracker url as used by Bugzilla.
        ext_bz_bug_id: A single external bug id or list of external bug ids
            (ie: the bug number in the external tracker).
        bug_ids: A single bug id or list of bug ids to have external tracker
            info updated.
        ext_status: The status of the external bug.
        ext_description: The description of the external bug.
        ext_priority: The priority of the external bug.
        """
        params = {}
        if ids is not None:
            params['ids'] = self._listify(ids)
        if ext_type_id is not None:
            params['ext_type_id'] = ext_type_id
        if ext_type_description is not None:
            params['ext_type_description'] = ext_type_description
        if ext_type_url is not None:
            params['ext_type_url'] = ext_type_url
        if ext_bz_bug_id is not None:
            params['ext_bz_bug_id'] = self._listify(ext_bz_bug_id)
        if bug_ids is not None:
            params['bug_ids'] = self._listify(bug_ids)
        if ext_status is not None:
            params['ext_status'] = ext_status
        if ext_description is not None:
            params['ext_description'] = ext_description
        if ext_priority is not None:
            params['ext_priority'] = ext_priority
        return self._proxy.ExternalBugs.update_external_bug(params)

    def remove_external_tracker(self, ids=None, ext_type_id=None,
                                ext_type_description=None, ext_type_url=None,
                                ext_bz_bug_id=None, bug_ids=None):
        """
        Wrapper method to allow removal of external tracking bugs using the
        ExternalBugs::WebService::remove_external_bug method.

        This is documented at
        https://bugzilla.redhat.com/docs/en/html/api/extensions/ExternalBugs/lib/WebService.html#remove_external_bug

        ids: A single external tracker bug id or list of external tracker bug
            ids.
        ext_type_id: The external tracker id as used by Bugzilla.
        ext_type_description: The external tracker description as used by
            Bugzilla.
        ext_type_url: The external tracker url as used by Bugzilla.
        ext_bz_bug_id: A single external bug id or list of external bug ids
            (ie: the bug number in the external tracker).
        bug_ids: A single bug id or list of bug ids to have external tracker
            info updated.
        """
        params = {}
        if ids is not None:
            params['ids'] = self._listify(ids)
        if ext_type_id is not None:
            params['ext_type_id'] = ext_type_id
        if ext_type_description is not None:
            params['ext_type_description'] = ext_type_description
        if ext_type_url is not None:
            params['ext_type_url'] = ext_type_url
        if ext_bz_bug_id is not None:
            params['ext_bz_bug_id'] = self._listify(ext_bz_bug_id)
        if bug_ids is not None:
            params['bug_ids'] = self._listify(bug_ids)
        return self._proxy.ExternalBugs.remove_external_bug(params)


    #################
    # Query methods #
    #################

    def pre_translation(self, query):
        '''Translates the query for possible aliases'''
        old = query.copy()

        if 'bug_id' in query:
            if not isinstance(query['bug_id'], list):
                query['id'] = query['bug_id'].split(',')
            else:
                query['id'] = query['bug_id']
            del query['bug_id']

        if 'component' in query:
            if not isinstance(query['component'], list):
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
            bug['components'] = isinstance(val, list) and val or [val]
            bug['component'] = bug['components'][0]

        if 'version' in bug and "versions" not in bug:
            val = bug['version']
            bug['versions'] = isinstance(val, list) and val or [val]
            bug['version'] = bug['versions'][0]

        # sub_components isn't too friendly of a format, add a simpler
        # sub_component value
        if 'sub_components' in bug and 'sub_component' not in bug:
            val = bug['sub_components']
            bug['sub_component'] = ""
            if isinstance(val, dict):
                values = []
                for vallist in val.values():
                    values += vallist
                bug['sub_component'] = " ".join(values)

        if not self.rhbz_back_compat:
            return

        if 'flags' in bug and isinstance(bug["flags"], list):
            tmpstr = []
            for tmp in bug['flags']:
                tmpstr.append("%s%s" % (tmp['name'], tmp['status']))

            bug['flags'] = ",".join(tmpstr)

        if 'blocks' in bug and isinstance(bug["blocks"], list):
            # Aliases will handle the 'blockedby' and 'blocked' back compat
            bug['blocks'] = ','.join([str(b) for b in bug['blocks']])

        if 'keywords' in bug and isinstance(bug["keywords"], list):
            bug['keywords'] = ','.join(bug['keywords'])

        if 'alias' in bug and isinstance(bug["alias"], list):
            bug['alias'] = ','.join(bug['alias'])

        if ('groups' in bug and
            isinstance(bug["groups"], list) and
            len(bug["groups"]) > 0 and
            isinstance(bug["groups"][0], str)):
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

    def build_external_tracker_boolean_query(
            self, ext_type_description=None, ext_type_url=None,
            ext_bz_bug_id=None, ext_status=None):
        """
        Helper method to build a boolean query to find bugs that contain an
        external tracker.

        All parameters that are None will be ignored when building the query.

        ext_type_description: The external tracker description as used by
            Bugzilla.
        ext_type_url: The external tracker url as used by Bugzilla.
        ext_bz_bug_id: The external bug id (ie: the bug number in the
            external tracker).
        ext_status: The status of the external bug.
        """
        parts = []

        if ext_type_description is not None:
            parts.append(
                'external_bugzilla.description-equals-{0:s}'.format(
                    ext_type_description))

        if ext_type_url is not None:
            parts.append(
                'external_bugzilla.url-equals-{0:s}'.format(ext_type_url))

        if ext_bz_bug_id is not None:
            id_str = str(ext_bz_bug_id)
            parts.append(
                'ext_bz_bug_map.ext_bz_bug_id-equals-{0:s}'.format(id_str))

        if ext_status is not None:
            parts.append(
                'ext_bz_bug_map.ext_status-equals-{0:s}'.format(ext_status))

        return ' & '.join(parts)

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
                    # pylint: disable=cell-var-from-loop
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
