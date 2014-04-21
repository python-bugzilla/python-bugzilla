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
    bz_ver_major = 4
    bz_ver_minor = 0


    #################
    # Query Methods #
    #################

    def build_query(self, **kwargs):
        query = Bugzilla36.build_query(self, **kwargs)

        # 'include_fields' only available for Bugzilla4+
        include_fields = self._convert_include_field_list(
            kwargs.pop('include_fields', None))
        if include_fields:
            if 'id' not in include_fields:
                include_fields.append('id')
            query["include_fields"] = include_fields

        exclude_fields = self._convert_include_field_list(
            kwargs.pop('exclude_fields', None))
        if exclude_fields:
            query["exclude_fields"] = exclude_fields

        return query


class Bugzilla42(Bugzilla4):
    bz_ver_minor = 2


class Bugzilla44(Bugzilla42):
    bz_ver_minor = 4
