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

    def clicomm(self, argstr, expectexc=False):
        comm = "bugzilla " + argstr

        bz = self.bzclass(url=self.url, cookiefile=None)
        if expectexc:
            self.assertRaises(RuntimeError, tests.clicomm, comm, bz)
        else:
            return tests.clicomm(comm, bz, returncliout=True)

    def _testBZClass(self):
        bz = Bugzilla(url=self.url, cookiefile=None)
        self.assertTrue(isinstance(bz, self.bzclass))

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

    def _testInfoVers(self, comp, mincount, expectstr):
        out = self.clicomm("info --versions \"%s\"" % comp).splitlines()
        self.assertTrue(len(out) >= mincount)
        if expectstr:
            self.assertTrue(expectstr in out)

    def _testInfoCompOwners(self, comp, expectstr):
        expectexc = (expectstr == "FAIL")
        out = self.clicomm("info --component_owners \"%s\"" %
                           comp, expectexc=expectexc)
        if expectexc:
            return
        self.assertTrue(expectstr in out.splitlines())


class BZ32(BaseTest):
    url = "https://bugzilla.kernel.org/xmlrpc.cgi"
    bzclass = bugzilla.Bugzilla32

    test0 = BaseTest._testBZClass
    test1 = lambda s: BaseTest._testInfoProducts(s, 10, "Virtualization")
    test2 = lambda s: BaseTest._testInfoComps(s, "Virtualization", 3, "kvm")
    test3 = lambda s: BaseTest._testInfoVers(s, "Virtualization", 0, None)
    test4 = lambda s: BaseTest._testInfoCompOwners(s, "Virtualization", "FAIL")


class RHTest(BaseTest):
    url = "https://bugzilla.redhat.com/xmlrpc.cgi"
    bzclass = bugzilla.RHBugzilla

    test0 = BaseTest._testBZClass
    test1 = lambda s: BaseTest._testInfoProducts(s, 125,
                                                 "Virtualization Tools")
    test2 = lambda s: BaseTest._testInfoComps(s, "Virtualization Tools",
                                              10, "virt-manager")
    test3 = lambda s: BaseTest._testInfoVers(s, "Fedora", 19, "rawhide")
    test4 = lambda s: BaseTest._testInfoCompOwners(s, "Virtualization Tools",
                                        "libvirt: Libvirt Maintainers")
