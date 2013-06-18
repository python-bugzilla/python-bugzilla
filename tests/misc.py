#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for building query strings with bin/bugzilla
'''

import atexit
import os
import shutil
import sys
import unittest

import bugzilla

import tests


class MiscCLI(unittest.TestCase):
    """
    Test miscellaneous CLI bits to get build out our code coverage
    """
    maxDiff = None

    def testManPageGeneration(self):
        try:
            # If logilab found, we get some useless import warning
            import warnings
            warnings.simplefilter("ignore")

            from logilab.common.optik_ext import ManHelpFormatter
            ignore = ManHelpFormatter
        except Exception, e:
            print "Skipping man page test: %s" % e
            return

        out = tests.clicomm("bugzilla --generate-man", None)
        self.assertTrue(len(out.splitlines()) > 100)

    def testHelp(self):
        out = tests.clicomm("bugzilla --help", None)
        self.assertTrue(len(out.splitlines()) > 18)

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

    def testCookies(self):
        if (sys.version_info[0] < 2 or
            (sys.version_info[0] == 2 and sys.version_info[1] < 6)):
            print "\npython too old, skipping cookie test"
            return

        cookiesbad = os.path.join(os.getcwd(), "tests/data/cookies-bad.txt")
        cookieslwp = os.path.join(os.getcwd(), "tests/data/cookies-lwp.txt")
        cookiesmoz = os.path.join(os.getcwd(), "tests/data/cookies-moz.txt")
        cookiesnew = cookieslwp + ".new"

        def cleanup():
            if os.path.exists(cookiesnew):
                os.unlink(cookiesnew)
        atexit.register(cleanup)
        shutil.copy(cookieslwp, cookiesnew)

        # Mozilla should be converted inplace to LWP
        bugzilla.Bugzilla3(url=None, cookiefile=cookiesnew)
        self.assertEquals(file(cookiesmoz).read(), file(cookiesnew).read())

        # Make sure bad cookies raise an error
        try:
            bugzilla.Bugzilla3(url=None, cookiefile=cookiesbad)
            raise AssertionError("Expected BugzillaError from parsing %s" %
                                 os.path.basename(cookiesbad))
        except bugzilla.BugzillaError:
            # Expected result
            pass

        # Mozilla should 'just work'
        bugzilla.Bugzilla3(url=None, cookiefile=cookiesmoz)

    def testPostTranslation(self):
        def _testPostCompare(bz, indict, outexpect):
            outdict = indict.copy()
            bz.post_translation({}, outdict)
            self.assertTrue(outdict == outexpect)

            # Make sure multiple calls don't change anything
            bz.post_translation({}, outdict)
            self.assertTrue(outdict == outexpect)

        bug3 = bugzilla.Bugzilla3(url=None, cookiefile=None)
        rhbz = bugzilla.RHBugzilla(url=None, cookiefile=None)

        test1 = {
            "component": ["comp1"],
            "version": ["ver1", "ver2"],

            'flags': [{
                'is_active': 1,
                'name': 'qe_test_coverage',
                'setter': 'pm-rhel@redhat.com',
                'status': '?',
            }, {
                'is_active': 1,
                'name': 'rhel-6.4.0',
                'setter': 'pm-rhel@redhat.com',
                'status': '+',
            }],

            'alias': ["FOO", "BAR"],
            'blocks': [782183, 840699, 923128],
            'keywords': ['Security'],
            'groups': ['redhat'],
        }

        out_simple = test1.copy()
        out_simple["components"] = out_simple["component"]
        out_simple["component"] = out_simple["components"][0]
        out_simple["versions"] = out_simple["version"]
        out_simple["version"] = out_simple["versions"][0]

        out_complex = out_simple.copy()
        out_complex["keywords"] = ",".join(out_complex["keywords"])
        out_complex["blocks"] = ",".join([str(b) for b in
                                          out_complex["blocks"]])
        out_complex["alias"] = ",".join(out_complex["alias"])
        out_complex["groups"] = [{'description': 'redhat',
                                  'ison': 1, 'name': 'redhat'}]
        out_complex["flags"] = "qe_test_coverage?,rhel-6.4.0+"

        _testPostCompare(bug3, test1, test1)
        _testPostCompare(rhbz, test1, out_simple)

        rhbz.rhbz_back_compat = True
        _testPostCompare(rhbz, test1, out_complex)
