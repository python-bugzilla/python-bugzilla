#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for building query strings with bin/bugzilla
'''

import unittest

import bugzilla

import tests


class MiscCLI(unittest.TestCase):
    """
    Test miscellaneous CLI bits to get build out our code coverage
    """
    maxDiff = None

    def testManPageGeneration(self):
        out = tests.clicomm("bugzilla --generate-man", None)
        self.assertTrue(len(out.splitlines()) > 100)

    def testHelp(self):
        out = tests.clicomm("bugzilla --help", None)
        self.assertTrue(len(out.splitlines()) > 20)

    def testCmdHelp(self):
        out = tests.clicomm("bugzilla query --help", None)
        self.assertTrue(len(out.splitlines()) > 40)

    def testVersion(self):
        out = tests.clicomm("bugzilla --version", None)
        self.assertTrue(len(out.splitlines()) >= 2)


class MiscAPI(unittest.TestCase):
    """
    Test miscellaneous API bits
    """
    def testUserAgent(self):
        b3 = bugzilla.Bugzilla3(url=None, cookiefile=None)
        rhbz = bugzilla.RHBugzilla(url=None, cookiefile=None)

        self.assertTrue(b3.user_agent.endswith("Bugzilla3/0.1"))
        self.assertTrue(rhbz.user_agent.endswith("RHBugzilla/0.1"))
