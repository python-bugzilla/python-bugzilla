# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

from .base import Bugzilla
from .rhbugzilla import RHBugzilla

# These are old compat classes. Nothing new should be added here,
# and these should not be altered


class Bugzilla3(Bugzilla):
    pass


class Bugzilla32(Bugzilla):
    pass


class Bugzilla34(Bugzilla):
    pass


class Bugzilla36(Bugzilla):
    pass


class Bugzilla4(Bugzilla):
    pass


class Bugzilla42(Bugzilla):
    pass


class Bugzilla44(Bugzilla):
    pass


class NovellBugzilla(Bugzilla):
    pass


class RHBugzilla3(RHBugzilla):
    pass


class RHBugzilla4(RHBugzilla):
    pass
