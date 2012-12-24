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
