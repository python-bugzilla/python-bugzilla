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


class Bugzilla42(Bugzilla4):
    bz_ver_minor = 2


class Bugzilla44(Bugzilla42):
    bz_ver_minor = 4
