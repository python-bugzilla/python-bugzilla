#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests that do permanent functional against a real bugzilla instances.
'''

import datetime
import os
import re
import unittest
import urllib2

import bugzilla
from bugzilla import Bugzilla

import tests


def _split_int(s):
    return [int(i) for i in s.split(",")]


class BaseTest(unittest.TestCase):
    url = None
    bzclass = None

    def _getCookiefile(self):
        return os.path.expanduser("~/.bugzillacookies")

    def _testBZClass(self):
        bz = Bugzilla(url=self.url, cookiefile=None)
        self.assertTrue(isinstance(bz, self.bzclass))

    def _testCookie(self):
        cookiefile = self._getCookiefile()
        domain = urllib2.urlparse.urlparse(self.url).netloc
        if os.path.exists(cookiefile):
            out = file(cookiefile).read(1024)
            if domain in out:
                return

        raise RuntimeError("%s must exist and contain domain '%s'" %
                           (cookiefile, domain))


class RHPartnerTest(BaseTest):
    # Despite its name, this instance is simply for bugzilla testing,
    # doesn't send out emails and is blown away occasionally. The front
    # page has some info.
    url = "https://partner-bugzilla.redhat.com/xmlrpc.cgi"
    bzclass = bugzilla.RHBugzilla

    test1 = BaseTest._testCookie
    test2 = BaseTest._testBZClass

    def test3NewBugBasic(self):
        """
        Create a bug with minimal amount of fields, then close it
        """

        component = "python-bugzilla"
        version = "16"
        summary = ("python-bugzilla test basic bug %s" %
                   datetime.datetime.today())
        newout = tests.clicomm("bugzilla new "
            "--product Fedora --component %s --version %s "
            "--summary \"%s\" "
            "--comment \"Test bug from the python-bugzilla test suite\" "
            "--outputformat \"%%{bug_id}\"" %
            (component, version, summary), bz)

        self.assertTrue(len(newout.splitlines()) == 3)

        bugid = int(newout.splitlines()[2])
        bug = bz.getbug(bugid)
        print "\nCreated bugid: %s" % bugid

        self.assertEquals(bug.component, [component])
        self.assertEquals(bug.version, [version])
        self.assertEquals(bug.summary, summary)

        # Close the bug
        tests.clicomm("bugzilla modify --close NOTABUG %s" % bugid,
                      bz)
        bug.refresh()
        self.assertEquals(bug.status, "CLOSED")
        self.assertEquals(bug.resolution, "NOTABUG")


    def test4NewBugAllFields(self):
        """
        Create a bug using all 'new' fields, check some values, close it
        """
        bz = self.bzclass(url=self.url, cookiefile=self._getCookiefile())

        summary = ("python-bugzilla test manyfields bug %s" %
                   datetime.datetime.today())
        url = "http://example.com"
        osval = "Windows"
        cc = "triage@lists.fedoraproject.org"
        blocked = "461686,461687"
        dependson = "427301"
        comment = "Test bug from python-bugzilla test suite"
        newout = tests.clicomm("bugzilla new "
            "--product Fedora --component python-bugzilla --version 16 "
            "--summary \"%s\" "
            "--comment \"%s\" "
            "--url %s --severity Urgent --priority Low --os %s "
            "--arch ppc --cc %s --blocked %s --dependson %s "
            "--outputformat \"%%{bug_id}\"" %
            (summary, comment, url, osval, cc, blocked, dependson), bz)

        self.assertTrue(len(newout.splitlines()) == 3)

        bugid = int(newout.splitlines()[2])
        bug = bz.getbug(bugid)
        print "\nCreated bugid: %s" % bugid

        # XXX: check full output for comment?
        self.assertEquals(bug.summary, summary)
        self.assertEquals(bug.bug_file_loc, url)
        self.assertEquals(bug.op_sys, osval)
        self.assertEquals(bug.blocks, _split_int(blocked))
        self.assertEquals(bug.depends_on, _split_int(dependson))
        self.assertTrue(all([e in bug.cc for e in cc.split(",")]))
        self.assertEquals(bug.longdescs[0]["body"], comment)

        # Close the bug
        tests.clicomm("bugzilla modify --close WONTFIX %s" % bugid,
                      bz)
        bug.refresh()
        self.assertEquals(bug.status, "CLOSED")
        self.assertEquals(bug.resolution, "WONTFIX")


    # XXX: Multiple modify tests, one for each action
    # XXX: Modify test for multiple bugs simultaneously
    # XXX: Modify test for multiple actions in one go

    def test5ModifyStatus(self):
        """
        Modify a bunch of bug fields for an existing bug, then put
        it back the way you found it
        """
        bz = self.bzclass(url=self.url, cookiefile=self._getCookiefile())
        bugid = "663674"
        cmd = "bugzilla modify %s " % bugid

        bug = bz.getbug(bugid)

        # We want to start with an open bug, so fix things
        if bug.status == "CLOSED":
            tests.clicomm(cmd + "--status ASSIGNED", bz)
            bug.refresh()
            self.assertEquals(bug.status, "ASSIGNED")

        origstatus = bug.status

        # Set to ON_QA with a private comment
        status = "ON_QA"
        comment = ("changing status to %s at %s" %
                   (status, datetime.datetime.today()))
        tests.clicomm(cmd +
            "--status %s --comment \"%s\" --private" % (status, comment), bz)

        bug.refresh()
        self.assertEquals(bug.status, status)
        self.assertEquals(bug.longdescs[-1]["isprivate"], 1)
        self.assertEquals(bug.longdescs[-1]["body"], comment)

        # Close bug as DEFERRED with a private comment
        resolution = "DEFERRED"
        comment = ("changing status to CLOSED=%s at %s" %
                   (resolution, datetime.datetime.today()))
        tests.clicomm(cmd +
            "--close %s --comment \"%s\" --private" %
            (resolution, comment), bz)

        bug.refresh()
        self.assertEquals(bug.status, "CLOSED")
        self.assertEquals(bug.resolution, resolution)
        self.assertEquals(bug.longdescs[-1]["isprivate"], 1)
        self.assertEquals(bug.longdescs[-1]["body"], comment)

        # Close bug as dup with no comment
        dupeid = "461686"
        desclen = len(bug.longdescs)
        tests.clicomm(cmd +
            "--close DUPLICATE --dupeid %s" % dupeid, bz)

        bug.refresh()
        self.assertEquals(bug.dupe_of, int(dupeid))
        self.assertEquals(len(bug.longdescs), desclen + 1)
        self.assertTrue(not bug.longdescs[-1]["body"])

        # Reset state
        tests.clicomm(cmd + "--status %s" % origstatus, bz)
        bug.refresh()
        self.assertEquals(bug.status, origstatus)
