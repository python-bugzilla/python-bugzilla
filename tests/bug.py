#
# Copyright Red Hat, Inc. 2014
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for testing some bug.py magic
'''

import unittest

from bugzilla import RHBugzilla
from bugzilla.bug import _Bug


rhbz = RHBugzilla(cookiefile=None)


class BugTest(unittest.TestCase):
    maxDiff = None
    bz = rhbz

    def testBasic(self):
        data = {
            "bug_id": 123456,
            "component": "foo",
            "product": "bar",
            "short_desc": "some short desc",
            "cf_fixed_in": "nope",
            "fixed_in": "1.2.3.4",
            "devel_whiteboard": "some status value",
        }

        bug = _Bug(bugzilla=self.bz, dict=data)

        self.assertEqual(hasattr(bug, "component"), True)
        self.assertEqual(getattr(bug, "components"), ["foo"])
        self.assertEqual(getattr(bug, "product"), "bar")
        self.assertEqual(hasattr(bug, "short_desc"), True)
        self.assertEqual(getattr(bug, "summary"), "some short desc")
        self.assertEqual(bool(getattr(bug, "cf_fixed_in")), True)
        self.assertEqual(getattr(bug, "fixed_in"), "1.2.3.4")
        self.assertEqual(bool(getattr(bug, "cf_devel_whiteboard")), True)
        self.assertEqual(getattr(bug, "devel_whiteboard"), "some status value")

        # This triggers some code in __getattr__
        dir(bug)
