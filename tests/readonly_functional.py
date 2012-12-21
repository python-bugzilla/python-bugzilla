#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests that do readonly functional tests against real bugzilla instances.
'''

import os
import re
import unittest

import bugzilla
from bugzilla import Bugzilla

import tests

class BaseTest(unittest.TestCase):
    url = None
    bzclass = None
    bz = None

    def clicomm(self, argstr, expectexc=False):
        comm = "bugzilla " + argstr

        if expectexc:
            self.assertRaises(RuntimeError, tests.clicomm, comm, self.bz)
        return tests.clicomm(comm, self._get_bz(), returncliout=True)

    def _get_bz(self):
        if self.bz is None:
            self.bz = Bugzilla(url=self.url, cookiefile=None)
            self.assertTrue(isinstance(self.bz, self.bzclass))
        return self.bz


    # Since we are running these tests against bugzilla instances in
    # the wild, we can't depend on certain data like product lists
    # remaining static. Use lax sanity checks in this case

    def _testInfoProducts(self, mincount, expectstr):
        out = self.clicomm("info --products").splitlines()
        self.assertTrue(len(out) >= mincount)
        self.assertTrue(expectstr in out)

    def _testInfoComps(self, comp, mincount, expectstr):
        out = self.clicomm("info --components \"%s\"" % comp).splitlines()
        self.assertTrue(len(out) >= mincount)
        self.assertTrue(expectstr in out)



class BZ32(BaseTest):
    url = "https://bugzilla.kernel.org/xmlrpc.cgi"
    bzclass = bugzilla.Bugzilla32

    test1 = lambda s: BaseTest._testInfoProducts(s, 10, "Virtualization")
    test2 = lambda s: BaseTest._testInfoComps(s, "Virtualization", 3, "kvm")


class RHTest(BaseTest):
    url = "https://bugzilla.redhat.com/xmlrpc.cgi"
    bzclass = bugzilla.RHBugzilla

    test1 = lambda s: BaseTest._testInfoProducts(s, 125,
                                                 "Virtualization Tools")
    #test2 = lambda s: BaseTest._testInfoComps(s, "Virtualization Tools",
    #                                          10, "virt-manager")
