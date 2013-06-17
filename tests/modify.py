#
# Copyright Red Hat, Inc. 2013
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for building update dictionaries with 'bugzilla modify'
'''

import unittest

from bugzilla.rhbugzilla import RHBugzilla

import tests


rhbz = RHBugzilla(cookiefile=None)


class ModifyTest(unittest.TestCase):
    maxDiff = None
    bz = rhbz

    def assertDictEqual(self, *args, **kwargs):
        # EPEL5 back compat
        if hasattr(unittest.TestCase, "assertDictEqual"):
            return unittest.TestCase.assertDictEqual(self, *args, **kwargs)
        return self.assertEqual(*args, **kwargs)

    def clicomm(self, argstr, out, flagsout=None):
        comm = "bugzilla modify --test-return-result 123456 224466 " + argstr

        if out is None:
            self.assertRaises(RuntimeError, tests.clicomm, comm, self.bz)
        else:
            (mdict, fdict) = tests.clicomm(comm, self.bz, returnmain=True)
            if flagsout:
                self.assertEqual(flagsout, fdict)
            else:
                self.assertDictEqual(out, mdict)

    def testBasic(self):
        self.clicomm(
            "--component foocomp --product barprod --status ASSIGNED "
            "--assignee foo@example.com --qa_contact bar@example.com "
            "--comment 'hey some comment'",
            {'assigned_to': 'foo@example.com',
             'comment': {'comment': 'hey some comment'},
             'component': 'foocomp',
             'product': 'barprod',
             'qa_contact': 'bar@example.com',
             'status': 'ASSIGNED'}
        )

    def testPrivateComment(self):
        self.clicomm(
            "--comment 'hey private comment' --private",
            {'comment': {'comment': 'hey private comment', 'is_private': True}}
        )

    def testClose(self):
        self.clicomm(
            "--close CANTFIX",
            {'resolution': 'CANTFIX', 'status': 'CLOSED'}
        )
        self.clicomm(
            "--dupeid 111333",
            {'dupe_of': 111333, 'resolution': 'DUPLICATE', 'status': 'CLOSED'}
        )

    def testFlags(self):
        self.clicomm(
            "--flag needinfoX --flag dev_ack+ --flag qa_ack-",
            {},
            [{'status': 'X', 'name': 'needinfo'},
             {'status': '+', 'name': 'dev_ack'},
             {'status': '-', 'name': 'qa_ack'}]
        )

    def testWhiteboard(self):
        # Whiteboard setting doesn't go through updatebugs, so this
        # expected to be empty
        self.clicomm(
            "--whiteboard tagfoo --whiteboard tagbar",
            {}
        )

    def testMisc(self):
        self.clicomm(
            "--fixed_in foo-bar-1.2.3",
            {"cf_fixed_in": "foo-bar-1.2.3"}
        )

    """
    def testDepends(self):
        self.clicomm(
            "--dependson 100 --dependson -200 --dependson +300",
            {}
        )
        self.clicomm(
            "--dependson =300",
            {}
        )
    """

    def testCC(self):
        self.clicomm(
            "--cc foo@example.com",
            {'cc': {'add': ['foo@example.com']}},
        )
