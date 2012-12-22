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
    closestatus = "CLOSED"

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

    def _testQuery(self, args, mincount, expectbug):
        expectexc = (expectbug == "FAIL")
        cli = "query %s --bug_status %s" % (args, self.closestatus)
        out = self.clicomm(cli, expectexc=expectexc)
        if expectexc:
            return

        self.assertTrue(len(out) >= mincount)
        self.assertTrue(any([l.startswith("#" + expectbug)
                             for l in out.splitlines()]))

        # Check --ids output option
        out2 = self.clicomm(cli + " --ids")
        self.assertTrue(len(out.splitlines()) == len(out2.splitlines()))
        self.assertTrue(any([l == expectbug for l in out2.splitlines()]))


    def _testQueryFull(self, bugid, mincount, expectstr):
        out = self.clicomm("query --full --bug_status %s --bug_id %s" %
                           (self.closestatus, bugid))

        self.assertTrue(len(out) >= mincount)
        self.assertTrue(expectstr in out)


class BZ32(BaseTest):
    url = "https://bugzilla.kernel.org/xmlrpc.cgi"
    bzclass = bugzilla.Bugzilla32

    """
    test0 = BaseTest._testBZClass
    test1 = lambda s: BaseTest._testInfoProducts(s, 10, "Virtualization")
    test2 = lambda s: BaseTest._testInfoComps(s, "Virtualization", 3, "kvm")
    test3 = lambda s: BaseTest._testInfoVers(s, "Virtualization", 0, None)
    test4 = lambda s: BaseTest._testInfoCompOwners(s, "Virtualization", "FAIL")

    # Querying was only supported as of bugzilla 3.4
    test5 = lambda s: BaseTest._testQuery(s, "--product Virtualization",
                                          0, "FAIL")
    """


class BZ34(BaseTest):
    url = "https://bugzilla.gnome.org/xmlrpc.cgi"
    bzclass = bugzilla.Bugzilla34
    closestatus = "RESOLVED"

    test0 = BaseTest._testBZClass
    test1 = lambda s: BaseTest._testQuery(s,
                "--product dogtail --component sniff",
                9, "321654")

    # BZ < 4 doesn't report values for --full


class BZ42(BaseTest):
    url = "https://bugzilla.freedesktop.org/xmlrpc.cgi"
    bzclass = bugzilla.Bugzilla4
    closestatus = "CLOSED,RESOLVED"

    test0 = BaseTest._testBZClass

    test1 = lambda s: BaseTest._testQuery(s, "--product avahi", 10, "3450")
    # XXX: Doesn't work, fails accessing bz.longdescs. Can prob be fixed
    #test2 = lambda s: BaseTest._testQueryFull(s, "3450", 10, "foo")


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

    test5 = lambda s: BaseTest._testQuery(s,
                "--product Fedora --component python-bugzilla --version 14",
                6, "621030")
    test6 = lambda s: BaseTest._testQueryFull(s, "663674", 70, "F14 is EOL.")
