#
# Copyright Red Hat, Inc. 2014
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for testing some bug.py magic
'''

import pickle
import sys
import unittest

import tests
from tests import StringIO

from bugzilla.bug import Bug


rhbz = tests.make_bz("4.4.0", rhbz=True)


class BugTest(unittest.TestCase):
    maxDiff = None
    bz = rhbz

    def testBasic(self):
        data = {
            "bug_id": 123456,
            "status": "NEW",
            "assigned_to": "foo@bar.com",
            "component": "foo",
            "product": "bar",
            "short_desc": "some short desc",
            "cf_fixed_in": "nope",
            "fixed_in": "1.2.3.4",
            "devel_whiteboard": "some status value",
        }

        bug = Bug(bugzilla=self.bz, dict=data)

        def _assert_bug():
            self.assertEqual(hasattr(bug, "component"), True)
            self.assertEqual(getattr(bug, "components"), ["foo"])
            self.assertEqual(getattr(bug, "product"), "bar")
            self.assertEqual(hasattr(bug, "short_desc"), True)
            self.assertEqual(getattr(bug, "summary"), "some short desc")
            self.assertEqual(bool(getattr(bug, "cf_fixed_in")), True)
            self.assertEqual(getattr(bug, "fixed_in"), "1.2.3.4")
            self.assertEqual(bool(getattr(bug, "cf_devel_whiteboard")), True)
            self.assertEqual(getattr(bug, "devel_whiteboard"),
                "some status value")

        _assert_bug()

        self.assertEqual(str(bug),
            "#123456 NEW        - foo@bar.com - some short desc")
        self.assertTrue(repr(bug).startswith("<Bug #123456"))

        # This triggers some code in __getattr__
        dir(bug)

        # Test special pickle support
        if hasattr(sys.version_info, "major") and sys.version_info.major >= 3:
            from io import BytesIO
            fd = BytesIO()
        else:
            fd = StringIO()

        pickle.dump(bug, fd)
        fd.seek(0)
        bug = pickle.load(fd)
        self.assertEqual(getattr(bug, "bugzilla"), None)
        bug.bugzilla = self.bz
        _assert_bug()

    def testBugNoID(self):
        try:
            Bug(bugzilla=self.bz, dict={"component": "foo"})
            raise AssertionError("Expected lack of ID failure.")
        except TypeError:
            pass
