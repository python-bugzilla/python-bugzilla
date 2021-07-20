#!/usr/bin/env python
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

# getbug.py: Simple demonstration of connecting to bugzilla, fetching
#            a bug, and printing some details.

import pprint

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
URL = "bugzilla.stage.redhat.com"

bzapi = bugzilla.Bugzilla(URL)

# getbug() is just a simple wrapper around getbugs(), which takes a list
# IDs, if you need to fetch multiple
#
# Example bug: https://bugzilla.stage.redhat.com/show_bug.cgi?id=427301
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
