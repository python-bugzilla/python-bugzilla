#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# getbug.py: Simple demonstration of connecting to bugzilla, fetching
#            a bug, and printing some details.

from __future__ import print_function

import pprint

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
URL = "partner-bugzilla.redhat.com"

bzapi = bugzilla.Bugzilla(URL)

# getbug() is just a simple wrapper around getbugs(), which takes a list
# IDs, if you need to fetch multiple
#
# Example bug: https://partner-bugzilla.redhat.com/show_bug.cgi?id=427301
bug = bzapi.getbug(427301)
print("Fetched bug #%s:" % bug.id)
print("  Product   = %s" % bug.product)
print("  Component = %s" % bug.component)
print("  Status    = %s" % bug.status)
print("  Resolution= %s" % bug.resolution)
print("  Summary   = %s" % bug.summary)

# Just check dir(bug) for other attributes, or check upstream bugzilla
# Bug.get docs for field names:
# https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#get-bug

# comments must be fetched separately on stock bugzilla. this just returns
# a raw dict with all the info.
comments = bug.getcomments()
print("\nLast comment data:\n%s" % pprint.pformat(comments[-1]))

# getcomments is just a wrapper around bzapi.get_comments(), which can be
# used for bulk comments fetching
