# bugzilla3.py - a Python interface to Bugzilla 3.x using xmlrpclib.
#
# Copyright (C) 2008, 2009 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from .base import BugzillaBase


class Bugzilla3(BugzillaBase):
    pass


class Bugzilla32(Bugzilla3):
    pass


class Bugzilla34(Bugzilla32):
    pass


class Bugzilla36(Bugzilla34):
    pass
