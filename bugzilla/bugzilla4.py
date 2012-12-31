#
# Copyright (C) 2008-2012 Red Hat Inc.
# Author: Michal Novotny <minovotn@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from bugzilla.bugzilla3 import Bugzilla36


class Bugzilla4(Bugzilla36):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 4.0.x releases.'''

    version = '0.1'

    bz_ver_major = 4
    bz_ver_minor = 0

    def __init__(self, **kwargs):
        Bugzilla36.__init__(self, **kwargs)


    #################
    # Query Methods #
    #################

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


    ############################
    # Bug modification methods #
    ############################

    def build_update(self,
                     alias=None,
                     assigned_to=None,
                     blocks_add=None,
                     blocks_remove=None,
                     blocks_set=None,
                     depends_on_add=None,
                     depends_on_remove=None,
                     depends_on_set=None,
                     cc_add=None,
                     cc_remove=None,
                     is_cc_accessible=None,
                     comment=None,
                     comment_private=None,
                     component=None,
                     deadline=None,
                     dupe_of=None,
                     estimated_time=None,
                     groups_add=None,
                     groups_remove=None,
                     keywords_add=None,
                     keywords_remove=None,
                     keywords_set=None,
                     op_sys=None,
                     platform=None,
                     priority=None,
                     product=None,
                     qa_contact=None,
                     is_creator_accessible=None,
                     remaining_time=None,
                     reset_assigned_to=None,
                     reset_qa_contact=None,
                     resolution=None,
                     see_also_add=None,
                     see_also_remove=None,
                     severity=None,
                     status=None,
                     summary=None,
                     target_milestone=None,
                     url=None,
                     version=None,
                     whiteboard=None,
                     work_time=None,
                     fixed_in=None,
                     qa_whiteboard=None,
                     devel_whiteboard=None,
                     internal_whiteboard=None):
        # pylint: disable=W0221
        # Argument number differs from overridden method
        # Base defines it with *args, **kwargs, so we don't have to maintain
        # the master argument list in 2 places
        ret = {}

        # These are only supported for rhbugzilla
        for key, val in [
            ("fixed_in", fixed_in),
            ("devel_whiteboard", devel_whiteboard),
            ("qa_whiteboard", qa_whiteboard),
            ("internal_whiteboard", internal_whiteboard),
        ]:
            if val is not None:
                raise ValueError("bugzilla instance does not support "
                                 "updating '%s'" % key)

        def s(key, val, convert=None):
            if val is None:
                return
            if convert:
                val = convert(val)
            ret[key] = val

        def add_dict(key, add, remove, _set=None, convert=None):
            if add is remove is _set is None:
                return

            def c(val):
                val = self._listify(val)
                if convert:
                    val = [convert(v) for v in val]
                return val

            newdict = {}
            if add is not None:
                newdict["add"] = c(add)
            if remove is not None:
                newdict["remove"] = c(remove)
            if _set is not None:
                newdict["set"] = c(_set)
            ret[key] = newdict


        s("alias", alias)
        s("assigned_to", assigned_to)
        s("is_cc_accessible", is_cc_accessible, bool)
        s("component", component)
        s("deadline", deadline)
        s("dupe_of", dupe_of, int)
        s("estimated_time", estimated_time, int)
        s("op_sys", op_sys)
        s("platform", platform)
        s("priority", priority)
        s("product", product)
        s("qa_contact", qa_contact)
        s("is_creator_accessible", is_creator_accessible, bool)
        s("remaining_time", remaining_time, float)
        s("reset_assigned_to", reset_assigned_to, bool)
        s("reset_qa_contact", reset_qa_contact, bool)
        s("resolution", resolution)
        s("severity", severity)
        s("status", status)
        s("summary", summary)
        s("target_milestone", target_milestone)
        s("url", url)
        s("version", version)
        s("whiteboard", whiteboard)
        s("work_time", work_time, float)

        add_dict("blocks", blocks_add, blocks_remove, blocks_set,
                 convert=int)
        add_dict("depends_on", depends_on_add, depends_on_remove,
                 depends_on_set, convert=int)
        add_dict("cc", cc_add, cc_remove)
        add_dict("groups", groups_add, groups_remove)
        add_dict("keywords", keywords_add, keywords_remove, keywords_set)
        add_dict("see_also", see_also_add, see_also_remove)

        if comment is not None:
            ret["comment"] = {"comment": comment}
            if comment_private:
                ret["comment"]["is_private"] = comment_private

        return ret


    def update_flags(self, idlist, flags):
        '''
        Updates the flags associated with a bug report.
        Format of flags is:
        [{"name": "needinfo", "status": "+", "requestee": "foo@bar.com"},
         {"name": "devel_ack", "status": "-"}, ...]
        '''
        d = {"ids": self._listify(idlist), "updates": flags}
        return self._proxy.Flag.update(d)



class Bugzilla42(Bugzilla4):
    bz_ver_minor = 2


class Bugzilla44(Bugzilla42):
    bz_ver_minor = 4
