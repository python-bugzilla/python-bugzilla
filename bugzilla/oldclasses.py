# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from .base import BugzillaBase
from .rhbugzilla import RHBugzilla


# These are old compat classes. Nothing new should be added here,
# and these should not be altered

class Bugzilla3(BugzillaBase): pass
class Bugzilla32(BugzillaBase): pass
class Bugzilla34(BugzillaBase): pass
class Bugzilla36(BugzillaBase): pass
class Bugzilla4(BugzillaBase): pass
class Bugzilla42(BugzillaBase): pass
class Bugzilla44(BugzillaBase): pass
class NovellBugzilla(BugzillaBase): pass
class RHBugzilla3(RHBugzilla): pass
class RHBugzilla4(RHBugzilla): pass
