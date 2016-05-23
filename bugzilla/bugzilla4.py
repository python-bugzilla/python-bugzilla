#
# Copyright (C) 2008-2012 Red Hat Inc.
# Author: Michal Novotny <minovotn@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from .bugzilla3 import Bugzilla36


class Bugzilla4(Bugzilla36):
    pass


class Bugzilla42(Bugzilla4):
    pass


class Bugzilla44(Bugzilla42):
    pass
