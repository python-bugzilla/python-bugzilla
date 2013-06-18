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

    def clicomm(self, argstr, out, flagsout=None, wbout=None):
        comm = "bugzilla modify --test-return-result 123456 224466 " + argstr

        if out is None:
            self.assertRaises(RuntimeError, tests.clicomm, comm, self.bz)
        else:
            (mdict, fdict, wdict) = tests.clicomm(comm,
                                                  self.bz, returnmain=True)
            if wbout:
                self.assertDictEqual(wbout, wdict)
            if flagsout:
                self.assertEqual(flagsout, fdict)
            if out:
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
        self.clicomm(
            "--whiteboard tagfoo --whiteboard -tagbar",
            {}, wbout={"status": (["tagfoo"], ["tagbar"])}
        )
        self.clicomm(
            "--whiteboard =foo --whiteboard =thisone",
            {'whiteboard': 'thisone'}
        )

        self.clicomm(
            "--qa_whiteboard =yo-qa --qa_whiteboard -foo "
            "--internal_whiteboard =internal-hey --internal_whiteboard +bar "
            "--devel_whiteboard =devel-duh --devel_whiteboard -yay",
            {'cf_devel_whiteboard': 'devel-duh',
             'cf_internal_whiteboard': 'internal-hey',
             'cf_qa_whiteboard': 'yo-qa'}, wbout={
            "qa": ([], ["foo"]),
            "internal": (["bar"], []),
            "devel": ([], ["yay"])},
        )

    def testMisc(self):
        self.clicomm(
            "--fixed_in foo-bar-1.2.3 --reset-qa-contact --reset-assignee",
            {"cf_fixed_in": "foo-bar-1.2.3",
             'reset_assigned_to': True,
             'reset_qa_contact': True}
        )
        self.clicomm(
            "--groups +foo --groups -bar,baz --groups fribby",
            {'groups': {'add': ['foo', 'fribby'], 'remove': ['bar', 'baz']}}
        )
        self.clicomm(
            "--target_milestone foomile --target_release relfoo",
            {"target_milestone": "foomile", "target_release": "relfoo"},
        )
        self.clicomm(
            "--priority medium --severity high",
            {"priority": "medium", "severity": "high"},
        )
        self.clicomm(
            "--os Windows --arch ia64 --version 1000 --url http://example.com "
            "--summary 'foo summary'",
            {"op_sys": "Windows", "platform": "ia64", "version": "1000",
             "url": "http://example.com", "summary": 'foo summary'},
        )

    def testDepends(self):
        self.clicomm(
            "--dependson 100,200",
            {'depends_on': {'add': [100, 200]}}
        )
        self.clicomm(
            "--dependson +100,200",
            {'depends_on': {'add': [100, 200]}}
        )
        self.clicomm(
            "--dependson -100,200",
            {'depends_on': {'remove': [100, 200]}}
        )
        self.clicomm(
            "--dependson =100,200",
            {'depends_on': {'set': [100, 200]}}
        )

        self.clicomm(
            "--dependson 1 --dependson -2 --dependson +3 --dependson =4",
            {'depends_on': {'add': [1, 3], 'remove': [2], 'set': [4]}}
        )
        self.clicomm(
            "--blocked 5 --blocked -6 --blocked +7 --blocked =8,9",
            {'blocks': {'add': [5, 7], 'remove': [6], 'set': [8, 9]}}
        )
        self.clicomm(
            "--keywords foo --keywords -bar --keywords +baz --keywords =yay",
            {'keywords': {'add': ["foo", "baz"],
                          'remove': ["bar"], 'set': ["yay"]}}
        )
        self.clicomm("--keywords =", {'keywords': {'set': []}})


    def testCC(self):
        self.clicomm(
            "--cc foo@example.com --cc -minus@example.com "
            "--cc =foo@example.com --cc +foo@example.com",
            {'cc': {'add': ['foo@example.com', "=foo@example.com",
                            "+foo@example.com"],
                    'remove': ["minus@example.com"]}},
        )
