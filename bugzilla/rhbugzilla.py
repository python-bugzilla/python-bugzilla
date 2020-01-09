# rhbugzilla.py - a Python interface to Red Hat Bugzilla using xmlrpclib.
#
# Copyright (C) 2008-2012 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

from logging import getLogger

from .base import Bugzilla
from ._util import listify

log = getLogger(__name__)


class RHBugzilla(Bugzilla):
    """
    Bugzilla class for connecting Red Hat's forked bugzilla instance,
    bugzilla.redhat.com

    Historically this class used many more non-upstream methods, but
    in 2012 RH started dropping most of its custom bits. By that time,
    upstream BZ had most of the important functionality.

    Much of the remaining code here is just trying to keep things operating
    in python-bugzilla back compatible manner.

    This class was written using bugzilla.redhat.com's API docs:
    https://bugzilla.redhat.com/docs/en/html/api/
    """
    def _init_class_state(self):
        def _add_both_alias(newname, origname):
            self._add_field_alias(newname, origname, is_api=False)
            self._add_field_alias(origname, newname, is_bug=False)

        _add_both_alias('fixed_in', 'cf_fixed_in')
        _add_both_alias('qa_whiteboard', 'cf_qa_whiteboard')
        _add_both_alias('devel_whiteboard', 'cf_devel_whiteboard')
        _add_both_alias('internal_whiteboard', 'cf_internal_whiteboard')

        self._add_field_alias('component', 'components', is_bug=False)
        self._add_field_alias('version', 'versions', is_bug=False)
        # Yes, sub_components is the field name the API expects
        self._add_field_alias('sub_components', 'sub_component', is_bug=False)

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
        # pylint: disable=arguments-differ
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
                component = listify(kwargs.get("component"))
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

        vals = Bugzilla.build_update(self, **kwargs)
        vals.update(adddict)

        return vals


    #################
    # Query methods #
    #################

    def pre_translation(self, query):
        """
        Translates the query for possible aliases
        """
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
        query.update(self._process_include_fields(query["include_fields"],
            None, None))

        if old != query:
            log.debug("RHBugzilla pretranslated query to: %s", query)

    def post_translation(self, query, bug):
        """
        Convert the results of getbug back to the ancient RHBZ value
        formats
        """
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
