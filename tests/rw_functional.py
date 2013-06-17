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
import random
import sys
import unittest
import urllib2

import bugzilla
from bugzilla import Bugzilla

import tests

cf = os.path.expanduser("~/.bugzillacookies")


def _split_int(s):
    return [int(i) for i in s.split(",")]


class BaseTest(unittest.TestCase):
    url = None
    bzclass = None

    def _testBZClass(self):
        bz = Bugzilla(url=self.url, cookiefile=None)
        self.assertTrue(isinstance(bz, self.bzclass))

    def _testCookie(self):
        cookiefile = cf
        domain = urllib2.urlparse.urlparse(self.url)[1]
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
    #url = "https://bzweb01-devel.app.eng.rdu.redhat.com/"
    bzclass = bugzilla.RHBugzilla


    def _check_have_admin(self, bz, funcname):
        # groupnames is empty for any user if our logged in user does not
        # have admin privs.
        # Check a known account that likely won't ever go away
        ret = bool(bz.getuser("anaconda-maint-list@redhat.com").groupnames)
        if not ret:
            print "\nNo admin privs, skipping %s" % funcname
        return ret

    def _check_rh_privs(self, bz, funcname, quiet=False):
        noprivs = bool(bz.getbugs([184858]) == [None])
        if noprivs and not quiet:
            print "\nNo RH privs, skipping %s" % funcname
        return not noprivs


    test1 = BaseTest._testCookie
    test2 = BaseTest._testBZClass


    def test3NewBugBasic(self):
        """
        Create a bug with minimal amount of fields, then close it
        """
        bz = self.bzclass(url=self.url, cookiefile=cf)
        component = "python-bugzilla"
        version = "rawhide"
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

        # Verify hasattr works
        self.assertTrue(hasattr(bug, "id"))
        self.assertTrue(hasattr(bug, "bug_id"))

        self.assertEquals(bug.component, component)
        self.assertEquals(bug.version, version)
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
        bz = self.bzclass(url=self.url, cookiefile=cf)

        summary = ("python-bugzilla test manyfields bug %s" %
                   datetime.datetime.today())
        url = "http://example.com"
        osval = "Windows"
        cc = "triage@lists.fedoraproject.org"
        blocked = "461686,461687"
        dependson = "427301"
        comment = "Test bug from python-bugzilla test suite"
        newout = tests.clicomm("bugzilla new "
            "--product Fedora --component python-bugzilla --version rawhide "
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

        self.assertEquals(bug.summary, summary)
        self.assertEquals(bug.bug_file_loc, url)
        self.assertEquals(bug.op_sys, osval)
        self.assertEquals(bug.blocks, _split_int(blocked))
        self.assertEquals(bug.depends_on, _split_int(dependson))
        self.assertTrue(all([e in bug.cc for e in cc.split(",")]))
        self.assertEquals(bug.longdescs[0]["text"], comment)

        # Close the bug
        tests.clicomm("bugzilla modify --close WONTFIX %s" % bugid,
                      bz)
        bug.refresh()
        self.assertEquals(bug.status, "CLOSED")
        self.assertEquals(bug.resolution, "WONTFIX")


    def test5ModifyStatus(self):
        """
        Modify status and comment fields for an existing bug
        """
        bz = self.bzclass(url=self.url, cookiefile=cf)
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
        self.assertEquals(bug.longdescs[-1]["is_private"], 1)
        self.assertEquals(bug.longdescs[-1]["text"], comment)

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
        self.assertEquals(bug.longdescs[-1]["is_private"], 1)
        self.assertEquals(bug.longdescs[-1]["text"], comment)

        # Close bug as dup with no comment
        dupeid = "461686"
        desclen = len(bug.longdescs)
        tests.clicomm(cmd +
            "--close DUPLICATE --dupeid %s" % dupeid, bz)

        bug.refresh()
        self.assertEquals(bug.dupe_of, int(dupeid))
        self.assertEquals(len(bug.longdescs), desclen + 1)
        self.assertTrue("marked as a duplicate" in bug.longdescs[-1]["text"])

        # Add lone comment
        comment = ("adding lone comment at %s" % datetime.datetime.today())
        tests.clicomm(cmd + "--comment \"%s\" --private" % comment, bz)

        bug.refresh()
        self.assertEquals(bug.longdescs[-1]["is_private"], 1)
        self.assertEquals(bug.longdescs[-1]["text"], comment)

        # Reset state
        tests.clicomm(cmd + "--status %s" % origstatus, bz)
        bug.refresh()
        self.assertEquals(bug.status, origstatus)


    def test6ModifyEmails(self):
        """
        Modify cc, assignee, qa_contact for existing bug
        """
        bz = self.bzclass(url=self.url, cookiefile=cf)
        bugid = "663674"
        cmd = "bugzilla modify %s " % bugid

        bug = bz.getbug(bugid)

        origcc = bug.cc

        # Test CC list and reset it
        email1 = "triage@lists.fedoraproject.org"
        email2 = "crobinso@redhat.com"
        bug.deletecc(origcc)
        tests.clicomm(cmd + "--cc %s --cc %s" % (email1, email2), bz)

        bug.refresh()
        self.assertTrue(email1 in bug.cc)
        self.assertTrue(email2 in bug.cc)
        self.assertEquals(len(bug.cc), 2)

        tests.clicomm(cmd + "--cc -%s" % email1, bz)
        bug.refresh()
        self.assertTrue(email1 not in bug.cc)

        # Test assigned target
        tests.clicomm(cmd + "--assignee %s" % email1, bz)
        bug.refresh()
        self.assertEquals(bug.assigned_to, email1)

        # Test QA target
        tests.clicomm(cmd + "--qa_contact %s" % email1, bz)
        bug.refresh()
        self.assertEquals(bug.qa_contact, email1)

        # Reset values
        bug.deletecc(bug.cc)
        tests.clicomm(cmd + "--reset-qa-contact --reset-assignee", bz)

        bug.refresh()
        self.assertEquals(bug.cc, [])
        self.assertEquals(bug.assigned_to, "wwoods@redhat.com")
        self.assertEquals(bug.qa_contact, "extras-qa@fedoraproject.org")


    def test7ModifyMultiFlags(self):
        """
        Modify flags and fixed_in for 2 bugs
        """
        bz = self.bzclass(url=self.url, cookiefile=cf)
        bugid1 = "461686"
        bugid2 = "461687"
        cmd = "bugzilla modify %s %s " % (bugid1, bugid2)

        def flagstr(b):
            ret = []
            for flag in b.flags:
                ret.append(flag["name"] + flag["status"])
            return " ".join(sorted(ret))

        def cleardict(b):
            clearflags = {}
            for flag in b.flags:
                clearflags[flag["name"]] = "X"
            return clearflags

        bug1 = bz.getbug(bugid1)
        if cleardict(bug1):
            bug1.updateflags(cleardict(bug1))
        bug2 = bz.getbug(bugid2)
        if cleardict(bug2):
            bug2.updateflags(cleardict(bug2))


        # Set flags and confirm
        setflags = "needinfo? requires_doc_text-"
        tests.clicomm(cmd +
            " ".join([(" --flag " + f) for f in setflags.split()]), bz)

        bug1.refresh()
        bug2.refresh()

        self.assertEquals(flagstr(bug1), setflags)
        self.assertEquals(flagstr(bug2), setflags)
        self.assertEquals(bug1.get_flags("needinfo")[0]["status"], "?")
        self.assertEquals(bug1.get_flag_status("requires_doc_text"), "-")

        # Clear flags
        if cleardict(bug1):
            bug1.updateflags(cleardict(bug1))
        bug1.refresh()
        if cleardict(bug2):
            bug2.updateflags(cleardict(bug2))
        bug2.refresh()

        self.assertEquals(cleardict(bug1), {})
        self.assertEquals(cleardict(bug2), {})

        # Set "Fixed In" field
        origfix1 = bug1.fixed_in
        origfix2 = bug2.fixed_in

        newfix = origfix1 and (origfix1 + "-new1") or "blippy1"
        if newfix == origfix2:
            newfix = origfix2 + "-2"

        tests.clicomm(cmd + "--fixed_in %s" % newfix, bz)

        bug1.refresh()
        bug2.refresh()
        self.assertEquals(bug1.fixed_in, newfix)
        self.assertEquals(bug2.fixed_in, newfix)

        # Reset fixed_in
        tests.clicomm(cmd + "--fixed_in \"-\"", bz)

        bug1.refresh()
        bug2.refresh()
        self.assertEquals(bug1.fixed_in, "-")
        self.assertEquals(bug2.fixed_in, "-")


    def test7ModifyMisc(self):
        bugid = "461686"
        cmd = "bugzilla modify %s " % bugid
        bz = self.bzclass(url=self.url, cookiefile=cf)
        bug = bz.getbug(bugid)

        # modify --dependson
        tests.clicomm(cmd + "--dependson 123456", bz)
        bug.refresh()
        self.assertTrue(123456 in bug.depends_on)
        tests.clicomm(cmd + "--dependson =111222", bz)
        bug.refresh()
        self.assertEquals([111222], bug.depends_on)
        tests.clicomm(cmd + "--dependson -111222", bz)
        bug.refresh()
        self.assertEquals([], bug.depends_on)

        # modify --blocked
        tests.clicomm(cmd + "--blocked 123,456", bz)
        bug.refresh()
        self.assertEquals([123, 456], bug.blocks)
        tests.clicomm(cmd + "--blocked =", bz)
        bug.refresh()
        self.assertEquals([], bug.blocks)

        # modify --keywords
        tests.clicomm(cmd + "--keywords +Documentation --keywords EasyFix", bz)
        bug.refresh()
        self.assertEquals(["Documentation", "EasyFix"], bug.keywords)
        tests.clicomm(cmd + "--keywords -EasyFix --keywords -Documentation",
                      bz)
        bug.refresh()
        self.assertEquals([], bug.keywords)

        # modify --target_release
        # modify --target_milestone
        targetbugid = 831888
        targetbug = bz.getbug(targetbugid)
        targetcmd = "bugzilla modify %s " % targetbugid
        tests.clicomm(targetcmd +
                      "--target_milestone beta --target_release 6.2", bz)
        targetbug.refresh()
        self.assertEquals(targetbug.target_milestone, "beta")
        self.assertEquals(targetbug.target_release, ["6.2"])
        tests.clicomm(targetcmd +
                      "--target_milestone rc --target_release 6.0", bz)
        targetbug.refresh()
        self.assertEquals(targetbug.target_milestone, "rc")
        self.assertEquals(targetbug.target_release, ["6.0"])

        # modify --priority
        # modify --severity
        tests.clicomm(cmd + "--priority low --severity high", bz)
        bug.refresh()
        self.assertEquals(bug.priority, "low")
        self.assertEquals(bug.severity, "high")
        tests.clicomm(cmd + "--priority medium --severity medium", bz)
        bug.refresh()
        self.assertEquals(bug.priority, "medium")
        self.assertEquals(bug.severity, "medium")

        # modify --os
        # modify --platform
        # modify --version
        tests.clicomm(cmd + "--version 18 --os Windows --arch ppc "
                            "--url http://example.com", bz)
        bug.refresh()
        self.assertEquals(bug.version, "18")
        self.assertEquals(bug.op_sys, "Windows")
        self.assertEquals(bug.platform, "ppc")
        self.assertEquals(bug.url, "http://example.com")
        tests.clicomm(cmd + "--version rawhide --os Linux --arch s390 "
                            "--url http://example.com/fribby", bz)
        bug.refresh()
        self.assertEquals(bug.version, "rawhide")
        self.assertEquals(bug.op_sys, "Linux")
        self.assertEquals(bug.platform, "s390")
        self.assertEquals(bug.url, "http://example.com/fribby")


    def test8Attachments(self):
        tmpdir = "__test_attach_output"
        if tmpdir in os.listdir("."):
            os.system("rm -r %s" % tmpdir)
        os.mkdir(tmpdir)
        os.chdir(tmpdir)

        try:
            self._test8Attachments()
        finally:
            os.chdir("..")
            os.system("rm -r %s" % tmpdir)

    def _test8Attachments(self):
        """
        Get and set attachments for a bug
        """
        bz = self.bzclass(url=self.url, cookiefile=cf)
        getallbugid = "663674"
        setbugid = "461686"
        cmd = "bugzilla attach "
        testfile = "../tests/data/bz-attach-get1.txt"

        # Add attachment as CLI option
        setbug = bz.getbug(setbugid)
        orignumattach = len(setbug.attachments)

        # Add attachment from CLI with mime guessing
        desc1 = "python-bugzilla cli upload %s" % datetime.datetime.today()
        out1 = tests.clicomm(cmd + "%s --description \"%s\" --file %s" %
                             (setbugid, desc1, testfile), bz)

        desc2 = "python-bugzilla cli upload %s" % datetime.datetime.today()
        out2 = tests.clicomm(cmd + "%s --file test --description \"%s\"" %
                             (setbugid, desc2), bz, stdin=open(testfile))

        # Expected output format:
        #   Created attachment <attachid> on bug <bugid>

        setbug.refresh()
        self.assertEquals(len(setbug.attachments), orignumattach + 2)
        self.assertEquals(setbug.attachments[-2]["description"], desc1)
        self.assertEquals(setbug.attachments[-2]["id"],
                          int(out1.splitlines()[2].split()[2]))
        self.assertEquals(setbug.attachments[-1]["description"], desc2)
        self.assertEquals(setbug.attachments[-1]["id"],
                          int(out2.splitlines()[2].split()[2]))
        attachid = setbug.attachments[-2]["id"]

        # Set attachment flags
        self.assertEquals(setbug.attachments[-1]["flags"], [])
        bz.updateattachmentflags(setbug.id, setbug.attachments[-1]["id"],
                                 "review", status="+")
        setbug.refresh()

        self.assertEquals(len(setbug.attachments[-1]["flags"]), 1)
        self.assertEquals(setbug.attachments[-1]["flags"][0]["name"], "review")
        self.assertEquals(setbug.attachments[-1]["flags"][0]["status"], "+")

        bz.updateattachmentflags(setbug.id, setbug.attachments[-1]["id"],
                                 "review", status="X")
        setbug.refresh()
        self.assertEquals(setbug.attachments[-1]["flags"], [])


        # Get attachment, verify content
        out = tests.clicomm(cmd + "--get %s" % attachid, bz).splitlines()

        # Expect format:
        #   Wrote <filename>
        fname = out[2].split()[1].strip()

        self.assertEquals(len(out), 3)
        self.assertEquals(fname, "bz-attach-get1.txt")
        self.assertEquals(file(fname).read(),
                          file(testfile).read())
        os.unlink(fname)

        # Get all attachments
        getbug = bz.getbug(getallbugid)
        numattach = len(getbug.attachments)
        out = tests.clicomm(cmd + "--getall %s" % getallbugid, bz).splitlines()

        self.assertEquals(len(out), numattach + 2)
        fnames = [l.split(" ", 1)[1].strip() for l in out[2:]]
        self.assertEquals(len(fnames), numattach)
        for f in fnames:
            if not os.path.exists(f):
                raise AssertionError("filename '%s' not found" % f)
            os.unlink(f)


    def test9Whiteboards(self):
        bz = self.bzclass(url=self.url, cookiefile=cf)
        bug_id = "663674"
        cmd = "bugzilla modify %s " % bug_id
        bug = bz.getbug(bug_id)

        # Set all whiteboards
        initval = str(random.randint(1, 1024))
        tests.clicomm(cmd +
                "--whiteboard =%sstatus "
                "--devel_whiteboard =%sdevel "
                "--internal_whiteboard '=%sinternal, security, foo security1' "
                "--qa_whiteboard =%sqa " %
                (initval, initval, initval, initval), bz)

        bug.refresh()
        self.assertEquals(bug.whiteboard, initval + "status")
        self.assertEquals(bug.qa_whiteboard, initval + "qa")
        self.assertEquals(bug.devel_whiteboard, initval + "devel")
        self.assertEquals(bug.internal_whiteboard,
                          initval + "internal, security, foo security1")

        # Modify whiteboards
        tests.clicomm(cmd +
                      "--whiteboard =foobar "
                      "--qa_whiteboard _app ", bz)
        bug.prependwhiteboard("pre-", "devel")

        bug.refresh()
        self.assertEquals(bug.qa_whiteboard, initval + "qa" + " _app")
        self.assertEquals(bug.devel_whiteboard, "pre- " + initval + "devel")
        self.assertEquals(bug.status_whiteboard, "foobar")

        # Verify that tag manipulation is smart about separator
        tests.clicomm(cmd +
                      "--qa_whiteboard -_app "
                      "--internal_whiteboard -security", bz)
        bug.refresh()

        self.assertEquals(bug.qa_whiteboard, initval + "qa")
        self.assertEquals(bug.internal_whiteboard,
                          initval + "internal, foo security1")

        bug.addtag("teststuff", "internal")
        bug.refresh()
        self.assertEquals(bug.internal_whiteboard,
                          initval + "internal, foo security1, teststuff")


        # Clear whiteboards
        bug.setwhiteboard("", "status")
        bug.setwhiteboard("", "qa")
        bug.setwhiteboard("", "devel")
        bug.setwhiteboard("", "internal")

        bug.refresh()
        self.assertEquals(bug.whiteboard, "")
        self.assertEquals(bug.qa_whiteboard, "")
        self.assertEquals(bug.devel_whiteboard, "")
        self.assertEquals(bug.internal_whiteboard, "")


    def test10Login(self):
        """
        Failed login test, gives us a bit more coverage
        """
        ret = tests.clicomm("bugzilla --bugzilla %s "
                            "--user foobar@example.com "
                            "--password foobar login" % self.url, None,
                            expectfail=True)
        self.assertTrue("Logging in... failed." in ret)


    def test11UserUpdate(self):
        # This won't work if run by the same user we are using
        bz = self.bzclass(url=self.url, cookiefile=cf)
        email = "anaconda-maint-list@redhat.com"
        group = "fedora_contrib"

        if not self._check_have_admin(bz, sys._getframe().f_code.co_name):
            return

        user = bz.getuser(email)
        self.assertTrue(group in user.groupnames)
        origgroups = user.groupnames

        # Remove the group
        bz.updateperms(email, "remove", [group])
        user.refresh()
        self.assertTrue(group not in user.groupnames)

        # Re add it
        bz.updateperms(email, "add", group)
        user.refresh()
        self.assertTrue(group in user.groupnames)

        # Set groups
        newgroups = user.groupnames[:]
        newgroups.remove(group)
        bz.updateperms(email, "set", newgroups)
        user.refresh()
        self.assertTrue(group not in user.groupnames)

        # Reset everything
        bz.updateperms(email, "set", origgroups)
        user.refresh()
        self.assertEqual(user.groupnames, origgroups)


    def test11ComponentEditing(self):
        bz = self.bzclass(url=self.url, cookiefile=cf)
        component = ("python-bugzilla-testcomponent-%s" %
                     str(random.randint(1, 1024 * 1024 * 1024)))
        basedata = {
            "product": "Virtualization Tools",
            "component": component,
        }

        if not self._check_have_admin(bz, sys._getframe().f_code.co_name):
            return


        def compare(data, newid):
            products = bz._proxy.Product.get({"names": [basedata["product"]]})
            compdata = None
            for c in products["products"][0]["components"]:
                if int(c["id"]) == int(newid):
                    compdata = c
                    break

            self.assertTrue(bool(compdata))
            self.assertEqual(data["component"], compdata["name"])
            self.assertEqual(data["description"], compdata["description"])
            self.assertEqual(data["initialowner"],
                             compdata["default_assigned_to"])
            self.assertEqual(data["initialqacontact"],
                             compdata["default_qa_contact"])


        # Create component
        data = basedata.copy()
        data.update({
            "description": "foo test bar",
            "initialowner": "crobinso@redhat.com",
            "initialqacontact": "extras-qa@fedoraproject.org",
            "initialcclist": ["wwoods@redhat.com", "toshio@fedoraproject.org"],
        })
        newid = bz.addcomponent(data)['id']
        compare(data, newid)

        # Edit component
        data = basedata.copy()
        data.update({
            "description": "hey new desc!",
            "initialowner": "extras-qa@fedoraproject.org",
            "initialqacontact": "virt-mgr-maint@redhat.com",
            "initialcclist": ["libvirt-maint@redhat.com",
                              "virt-maint@lists.fedoraproject.org"],
        })
        bz.editcomponent(data)
        compare(data, newid)

    def test12SetCookie(self):
        bz = self.bzclass(url=self.url, cookiefile=cf)
        if not self._check_rh_privs(bz, sys._getframe().f_code.co_name):
            return

        try:
            bz.cookiefile = None
            raise AssertionError("Setting cookiefile for active connection "
                                 "should fail.")
        except RuntimeError, e:
            self.assertTrue("disconnect()" in str(e))

        bz.disconnect()
        bz.cookiefile = None
        bz.connect()
        self.assertFalse(bool(self._check_rh_privs(bz, "", True)))
