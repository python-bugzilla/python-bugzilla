#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests that do permanent functional against a real bugzilla instances.
'''

from __future__ import print_function

import datetime
import os
import random
import sys
import unittest

if hasattr(sys.version_info, "major") and sys.version_info.major >= 3:
    # pylint: disable=F0401,E0611
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

import bugzilla
from bugzilla import Bugzilla
from bugzilla.transport import _BugzillaToken

import tests

cf = os.path.expanduser("~/.bugzillacookies")
tf = os.path.expanduser("~/.bugzillatoken")


def _split_int(s):
    return [int(i) for i in s.split(",")]


class BaseTest(unittest.TestCase):
    url = None
    bzclass = None

    def _testBZClass(self):
        bz = Bugzilla(url=self.url, use_creds=False)
        self.assertTrue(bz.__class__ is self.bzclass)

    def _testCookieOrToken(self):
        domain = urlparse(self.url)[1]
        if os.path.exists(cf):
            out = open(cf).read(1024)
            if domain in out:
                return

        if os.path.exists(tf):
            token = _BugzillaToken(self.url, tokenfilename=tf)
            if token.value is not None:
                return

        raise RuntimeError("%s or %s must exist and contain domain '%s'" %
                           (cf, tf, domain))


class RHPartnerTest(BaseTest):
    # Despite its name, this instance is simply for bugzilla testing,
    # doesn't send out emails and is blown away occasionally. The front
    # page has some info.
    url = tests.REDHAT_URL or "partner-bugzilla.redhat.com"
    bzclass = bugzilla.RHBugzilla


    def _check_have_admin(self, bz, funcname):
        # groupnames is empty for any user if our logged in user does not
        # have admin privs.
        # Check a known account that likely won't ever go away
        ret = bool(bz.getuser("anaconda-maint-list@redhat.com").groupnames)
        if not ret:
            print("\nNo admin privs, reduced testing of %s" % funcname)
        return ret

    test2 = BaseTest._testBZClass


    def test00LoginState(self):
        bz = self.bzclass(url=self.url)
        self.assertTrue(bz.logged_in,
            "R/W tests require cached login credentials for url=%s" % self.url)

        bz = self.bzclass(url=self.url, use_creds=False)
        self.assertFalse(bz.logged_in,
            "Login state check failed for logged out user.")


    def test03NewBugBasic(self):
        """
        Create a bug with minimal amount of fields, then close it
        """
        bz = self.bzclass(url=self.url)
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
        print("\nCreated bugid: %s" % bugid)

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


    def test04NewBugAllFields(self):
        """
        Create a bug using all 'new' fields, check some values, close it
        """
        bz = self.bzclass(url=self.url)

        summary = ("python-bugzilla test manyfields bug %s" %
                   datetime.datetime.today())
        url = "http://example.com"
        osval = "Windows"
        cc = "triage@lists.fedoraproject.org"
        blocked = "461686,461687"
        dependson = "427301"
        comment = "Test bug from python-bugzilla test suite"
        sub_component = "Command-line tools (RHEL6)"
        alias = "pybz-%s" % datetime.datetime.today().strftime("%s")
        newout = tests.clicomm("bugzilla new "
            "--product 'Red Hat Enterprise Linux 6' --version 6.0 "
            "--component lvm2 --sub-component '%s' "
            "--summary \"%s\" "
            "--comment \"%s\" "
            "--url %s --severity Urgent --priority Low --os %s "
            "--arch ppc --cc %s --blocked %s --dependson %s "
            "--alias %s "
            "--outputformat \"%%{bug_id}\"" %
            (sub_component, summary, comment, url,
             osval, cc, blocked, dependson, alias), bz)

        self.assertTrue(len(newout.splitlines()) == 3)

        bugid = int(newout.splitlines()[2])
        bug = bz.getbug(bugid, extra_fields=["sub_components"])
        print("\nCreated bugid: %s" % bugid)

        self.assertEquals(bug.summary, summary)
        self.assertEquals(bug.bug_file_loc, url)
        self.assertEquals(bug.op_sys, osval)
        self.assertEquals(bug.blocks, _split_int(blocked))
        self.assertEquals(bug.depends_on, _split_int(dependson))
        self.assertTrue(all([e in bug.cc for e in cc.split(",")]))
        self.assertEquals(bug.longdescs[0]["text"], comment)
        self.assertEquals(bug.sub_components, {"lvm2": [sub_component]})
        self.assertEquals(bug.alias, [alias])

        # Close the bug

        # RHBZ makes it difficult to provide consistent semantics for
        # 'alias' update:
        # https://bugzilla.redhat.com/show_bug.cgi?id=1173114
        # alias += "-closed"
        tests.clicomm("bugzilla modify "
            "--close WONTFIX %s " %
            bugid, bz)
        bug.refresh()
        self.assertEquals(bug.status, "CLOSED")
        self.assertEquals(bug.resolution, "WONTFIX")
        self.assertEquals(bug.alias, [alias])

        # Check bug's minimal history
        ret = bug.get_history_raw()
        self.assertTrue(len(ret["bugs"]) == 1)
        self.assertTrue(len(ret["bugs"][0]["history"]) == 1)


    def test05ModifyStatus(self):
        """
        Modify status and comment fields for an existing bug
        """
        bz = self.bzclass(url=self.url)
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
        self.assertEquals(bug.comments[-1]["is_private"], 1)
        self.assertEquals(bug.comments[-1]["text"], comment)

        # Close bug as dup with no comment
        dupeid = "461686"
        desclen = len(bug.longdescs)
        tests.clicomm(cmd +
            "--close DUPLICATE --dupeid %s" % dupeid, bz)

        bug.refresh()
        self.assertEquals(bug.dupe_of, int(dupeid))
        self.assertEquals(len(bug.longdescs), desclen + 1)
        self.assertTrue("marked as a duplicate" in bug.longdescs[-1]["text"])

        # bz.setstatus test
        comment = ("adding lone comment at %s" % datetime.datetime.today())
        bug.setstatus("POST", comment=comment, private=True)
        bug.refresh()
        self.assertEquals(bug.longdescs[-1]["is_private"], 1)
        self.assertEquals(bug.longdescs[-1]["text"], comment)
        self.assertEquals(bug.status, "POST")

        # bz.close test
        fixed_in = str(datetime.datetime.today())
        bug.close("ERRATA", fixedin=fixed_in)
        bug.refresh()
        self.assertEquals(bug.status, "CLOSED")
        self.assertEquals(bug.resolution, "ERRATA")
        self.assertEquals(bug.fixed_in, fixed_in)

        # bz.addcomment test
        comment = ("yet another test comment %s" % datetime.datetime.today())
        bug.addcomment(comment, private=False)
        bug.refresh()
        self.assertEquals(bug.longdescs[-1]["text"], comment)
        self.assertEquals(bug.longdescs[-1]["is_private"], 0)

        # Confirm comments is same as getcomments
        self.assertEquals(bug.comments, bug.getcomments())

        # Reset state
        tests.clicomm(cmd + "--status %s" % origstatus, bz)
        bug.refresh()
        self.assertEquals(bug.status, origstatus)


    def test06ModifyEmails(self):
        """
        Modify cc, assignee, qa_contact for existing bug
        """
        bz = self.bzclass(url=self.url)
        bugid = "663674"
        cmd = "bugzilla modify %s " % bugid

        bug = bz.getbug(bugid)

        origcc = bug.cc

        # Test CC list and reset it
        email1 = "triage@lists.fedoraproject.org"
        email2 = "crobinso@redhat.com"
        bug.deletecc(origcc)
        tests.clicomm(cmd + "--cc %s --cc %s" % (email1, email2), bz)
        bug.addcc(email1)

        bug.refresh()
        self.assertTrue(email1 in bug.cc)
        self.assertTrue(email2 in bug.cc)
        self.assertEquals(len(bug.cc), 2)

        tests.clicomm(cmd + "--cc=-%s" % email1, bz)
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
        self.assertEquals(bug.assigned_to, "crobinso@redhat.com")
        self.assertEquals(bug.qa_contact, "extras-qa@fedoraproject.org")


    def test07ModifyMultiFlags(self):
        """
        Modify flags and fixed_in for 2 bugs
        """
        bz = self.bzclass(url=self.url)
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

        tests.clicomm(cmd + "--fixed_in=%s" % newfix, bz)

        bug1.refresh()
        bug2.refresh()
        self.assertEquals(bug1.fixed_in, newfix)
        self.assertEquals(bug2.fixed_in, newfix)

        # Reset fixed_in
        tests.clicomm(cmd + "--fixed_in=\"-\"", bz)

        bug1.refresh()
        bug2.refresh()
        self.assertEquals(bug1.fixed_in, "-")
        self.assertEquals(bug2.fixed_in, "-")


    def test07ModifyMisc(self):
        bugid = "461686"
        cmd = "bugzilla modify %s " % bugid
        bz = self.bzclass(url=self.url)
        bug = bz.getbug(bugid)

        # modify --dependson
        tests.clicomm(cmd + "--dependson 123456", bz)
        bug.refresh()
        self.assertTrue(123456 in bug.depends_on)
        tests.clicomm(cmd + "--dependson =111222", bz)
        bug.refresh()
        self.assertEquals([111222], bug.depends_on)
        tests.clicomm(cmd + "--dependson=-111222", bz)
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
        tests.clicomm(cmd + "--keywords=-EasyFix --keywords=-Documentation",
                      bz)
        bug.refresh()
        self.assertEquals([], bug.keywords)

        # modify --target_release
        # modify --target_milestone
        targetbugid = 492463
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
        tests.clicomm(cmd + "--version rawhide --os Windows --arch ppc "
                            "--url http://example.com", bz)
        bug.refresh()
        self.assertEquals(bug.version, "rawhide")
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

        # modify --field
        tests.clicomm(cmd + "--field cf_fixed_in=foo-bar-1.2.3 \
                      --field=cf_release_notes=baz", bz)

        bug.refresh()
        self.assertEquals(bug.fixed_in, "foo-bar-1.2.3")
        self.assertEquals(bug.cf_release_notes, "baz")


    def test08Attachments(self):
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
        bz = self.bzclass(url=self.url)
        getallbugid = "663674"
        setbugid = "461686"
        cmd = "bugzilla attach "
        testfile = "../tests/data/bz-attach-get1.txt"

        # Add attachment as CLI option
        setbug = bz.getbug(setbugid, extra_fields=["attachments"])
        orignumattach = len(setbug.attachments)

        # Add attachment from CLI with mime guessing
        desc1 = "python-bugzilla cli upload %s" % datetime.datetime.today()
        out1 = tests.clicomm(cmd + "%s --description \"%s\" --file %s" %
                             (setbugid, desc1, testfile), bz)

        desc2 = "python-bugzilla cli upload %s" % datetime.datetime.today()
        out2 = tests.clicomm(cmd + "%s --file test --summary \"%s\"" %
                             (setbugid, desc2), bz, stdin=open(testfile))

        # Expected output format:
        #   Created attachment <attachid> on bug <bugid>

        setbug.refresh()
        self.assertEquals(len(setbug.attachments), orignumattach + 2)
        self.assertEquals(setbug.attachments[-2]["summary"], desc1)
        self.assertEquals(setbug.attachments[-2]["id"],
                          int(out1.splitlines()[2].split()[2]))
        self.assertEquals(setbug.attachments[-1]["summary"], desc2)
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
        self.assertEquals(open(fname).read(),
                          open(testfile).read())
        os.unlink(fname)

        # Get all attachments
        getbug = bz.getbug(getallbugid)
        getbug.autorefresh = True
        numattach = len(getbug.attachments)
        out = tests.clicomm(cmd + "--getall %s" % getallbugid, bz).splitlines()

        self.assertEquals(len(out), numattach + 2)
        fnames = [l.split(" ", 1)[1].strip() for l in out[2:]]
        self.assertEquals(len(fnames), numattach)
        for f in fnames:
            if not os.path.exists(f):
                raise AssertionError("filename '%s' not found" % f)
            os.unlink(f)


    def test09Whiteboards(self):
        bz = self.bzclass(url=self.url)
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
                      "--qa_whiteboard _app "
                      "--devel_whiteboard =pre-%s" % bug.devel_whiteboard, bz)

        bug.refresh()
        self.assertEquals(bug.qa_whiteboard, initval + "qa" + " _app")
        self.assertEquals(bug.devel_whiteboard, "pre-" + initval + "devel")
        self.assertEquals(bug.status_whiteboard, "foobar")

        # Verify that tag manipulation is smart about separator
        tests.clicomm(cmd +
                      "--qa_whiteboard=-_app "
                      "--internal_whiteboard=-security,", bz)
        bug.refresh()

        self.assertEquals(bug.qa_whiteboard, initval + "qa")
        self.assertEquals(bug.internal_whiteboard,
                          initval + "internal, foo security1")

        # Clear whiteboards
        update = bz.build_update(
            whiteboard="", devel_whiteboard="",
            internal_whiteboard="", qa_whiteboard="")
        bz.update_bugs(bug.id, update)

        bug.refresh()
        self.assertEquals(bug.whiteboard, "")
        self.assertEquals(bug.qa_whiteboard, "")
        self.assertEquals(bug.devel_whiteboard, "")
        self.assertEquals(bug.internal_whiteboard, "")


    def test10Login(self):
        """
        Failed login test, gives us a bit more coverage
        """
        # We overwrite getpass for testing
        import getpass

        def fakegetpass(prompt):
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return sys.stdin.readline()
        oldgetpass = getpass.getpass
        getpass.getpass = fakegetpass

        try:
            # Implied login with --username and --password
            ret = tests.clicomm("bugzilla --bugzilla %s "
                                "--user foobar@example.com "
                                "--password foobar query -b 123456" % self.url,
                                None, expectfail=True)
            self.assertTrue("Login failed: " in ret)

            # 'login' with explicit options
            ret = tests.clicomm("bugzilla --bugzilla %s "
                                "--user foobar@example.com "
                                "--password foobar login" % self.url,
                                None, expectfail=True)
            self.assertTrue("Login failed: " in ret)

            # 'login' with positional options
            ret = tests.clicomm("bugzilla --bugzilla %s "
                                "login foobar@example.com foobar" % self.url,
                                None, expectfail=True)
            self.assertTrue("Login failed: " in ret)


            # bare 'login'
            stdinstr = "foobar@example.com\n\rfoobar\n\r"
            ret = tests.clicomm("bugzilla --bugzilla %s login" % self.url,
                                None, expectfail=True, stdinstr=stdinstr)
            self.assertTrue("Bugzilla Username:" in ret)
            self.assertTrue("Bugzilla Password:" in ret)
            self.assertTrue("Login failed: " in ret)
        finally:
            getpass.getpass = oldgetpass


    def test11UserUpdate(self):
        # This won't work if run by the same user we are using
        bz = self.bzclass(url=self.url)
        email = "anaconda-maint-list@redhat.com"
        group = "fedora_contrib"

        fn = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        have_admin = self._check_have_admin(bz, fn)

        user = bz.getuser(email)
        if have_admin:
            self.assertTrue(group in user.groupnames)
        origgroups = user.groupnames

        # Remove the group
        try:
            bz.updateperms(email, "remove", [group])
            user.refresh()
            self.assertTrue(group not in user.groupnames)
        except:
            e = sys.exc_info()[1]
            if have_admin:
                raise
            self.assertTrue("Sorry, you aren't a member" in str(e))

        # Re add it
        try:
            bz.updateperms(email, "add", group)
            user.refresh()
            self.assertTrue(group in user.groupnames)
        except:
            e = sys.exc_info()[1]
            if have_admin:
                raise
            self.assertTrue("Sorry, you aren't a member" in str(e))

        # Set groups
        try:
            newgroups = user.groupnames[:]
            if have_admin:
                newgroups.remove(group)
            bz.updateperms(email, "set", newgroups)
            user.refresh()
            self.assertTrue(group not in user.groupnames)
        except:
            e = sys.exc_info()[1]
            if have_admin:
                raise
            self.assertTrue("Sorry, you aren't a member" in str(e))

        # Reset everything
        try:
            bz.updateperms(email, "set", origgroups)
        except:
            e = sys.exc_info()[1]
            if have_admin:
                raise
            self.assertTrue("Sorry, you aren't a member" in str(e))

        user.refresh()
        self.assertEqual(user.groupnames, origgroups)


    def test11ComponentEditing(self):
        bz = self.bzclass(url=self.url)
        component = ("python-bugzilla-testcomponent-%s" %
                     str(random.randint(1, 1024 * 1024 * 1024)))
        basedata = {
            "product": "Fedora Documentation",
            "component": component,
        }

        fn = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        have_admin = self._check_have_admin(bz, fn)

        def compare(data, newid):
            proxy = bz._proxy  # pylint: disable=protected-access
            products = proxy.Product.get({"names": [basedata["product"]]})
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
            self.assertEqual(data["is_active"], compdata["is_active"])


        # Create component
        data = basedata.copy()
        data.update({
            "description": "foo test bar",
            "initialowner": "crobinso@redhat.com",
            "initialqacontact": "extras-qa@fedoraproject.org",
            "initialcclist": ["wwoods@redhat.com", "toshio@fedoraproject.org"],
            "is_active": True,
        })
        try:
            newid = bz.addcomponent(data)['id']
            print("Created product=%s component=%s" % (
                basedata["product"], basedata["component"]))
            compare(data, newid)
        except:
            e = sys.exc_info()[1]
            if have_admin:
                raise
            self.assertTrue("Sorry, you aren't a member" in str(e))


        # Edit component
        data = basedata.copy()
        data.update({
            "description": "hey new desc!",
            "initialowner": "extras-qa@fedoraproject.org",
            "initialqacontact": "virt-mgr-maint@redhat.com",
            "initialcclist": ["libvirt-maint@redhat.com",
                              "virt-maint@lists.fedoraproject.org"],
            "is_active": False,
        })
        try:
            bz.editcomponent(data)
            compare(data, newid)
        except:
            e = sys.exc_info()[1]
            if have_admin:
                raise
            self.assertTrue("Sorry, you aren't a member" in str(e))

    def test12SetCookie(self):
        bz = self.bzclass(self.url,
            cookiefile=-1, tokenfile=None)

        try:
            bz.cookiefile = None
            raise AssertionError("Setting cookiefile for active connection "
                                 "should fail.")
        except RuntimeError:
            e = sys.exc_info()[1]
            self.assertTrue("disconnect()" in str(e))

        bz.disconnect()
        bz.cookiefile = None
        bz.connect()
        self.assertFalse(bz.logged_in)

    def test13SubComponents(self):
        bz = self.bzclass(url=self.url)
        # Long closed RHEL5 lvm2 bug. This component has sub_components
        bug = bz.getbug("185526")
        bug.autorefresh = True
        self.assertEquals(bug.component, "lvm2")

        bz.update_bugs(bug.id, bz.build_update(
            component="lvm2", sub_component="Command-line tools (RHEL5)"))
        bug.refresh()
        self.assertEqual(bug.sub_components,
            {"lvm2": ["Command-line tools (RHEL5)"]})

        bz.update_bugs(bug.id, bz.build_update(sub_component={}))
        bug.refresh()
        self.assertEqual(bug.sub_components, {})

    def test13ExternalTrackerQuery(self):
        bz = self.bzclass(url=self.url)
        self.assertRaises(RuntimeError,
                          bz.build_external_tracker_boolean_query)

    def _deleteAllExistingExternalTrackers(self, bugid):
        bz = self.bzclass(url=self.url)
        ids = [bug['id'] for bug in bz.getbug(bugid).external_bugs]
        if ids != []:
            bz.remove_external_tracker(ids=ids)

    def test14ExternalTrackersAddUpdateRemoveQuery(self):
        bz = self.bzclass(url=self.url)
        bugid = 461686
        ext_bug_id = 380489

        # Delete any existing external trackers to get to a known state
        self._deleteAllExistingExternalTrackers(bugid)

        url = "https://bugzilla.mozilla.org"
        if bz.bz_ver_major < 5:
            url = "http://bugzilla.mozilla.org"

        # test adding tracker
        kwargs = {
            'ext_type_id': 6,
            'ext_type_url': url,
            'ext_type_description': 'Mozilla Foundation',
            'ext_status': 'Original Status',
            'ext_description': 'the description',
            'ext_priority': 'the priority'
        }
        bz.add_external_tracker(bugid, ext_bug_id, **kwargs)
        added_bug = bz.getbug(bugid).external_bugs[0]
        assert added_bug['type']['id'] == kwargs['ext_type_id']
        assert added_bug['type']['url'] == kwargs['ext_type_url']
        assert (added_bug['type']['description'] ==
            kwargs['ext_type_description'])
        assert added_bug['ext_status'] == kwargs['ext_status']
        assert added_bug['ext_description'] == kwargs['ext_description']
        assert added_bug['ext_priority'] == kwargs['ext_priority']

        # test updating status, description, and priority by id
        kwargs = {
            'ids': bz.getbug(bugid).external_bugs[0]['id'],
            'ext_status': 'New Status',
            'ext_description': 'New Description',
            'ext_priority': 'New Priority'
        }
        bz.update_external_tracker(**kwargs)
        updated_bug = bz.getbug(bugid).external_bugs[0]
        assert updated_bug['ext_bz_bug_id'] == str(ext_bug_id)
        assert updated_bug['ext_status'] == kwargs['ext_status']
        assert updated_bug['ext_description'] == kwargs['ext_description']
        assert updated_bug['ext_priority'] == kwargs['ext_priority']

        # test removing tracker
        ids = [bug['id'] for bug in bz.getbug(bugid).external_bugs]
        assert len(ids) == 1
        bz.remove_external_tracker(ids=ids)
        ids = [bug['id'] for bug in bz.getbug(bugid).external_bugs]
        assert len(ids) == 0

    def test15EnsureLoggedIn(self):
        bz = self.bzclass(url=self.url)
        comm = "bugzilla --ensure-logged-in query --bug_id 979546"
        tests.clicomm(comm, bz)

    def test16ModifyTags(self):
        bugid = "461686"
        cmd = "bugzilla modify %s " % bugid
        bz = self.bzclass(url=self.url)
        bug = bz.getbug(bugid)

        if bug.tags:
            bz.update_tags(bug.id, tags_remove=bug.tags)
            bug.refresh()
            self.assertEquals(bug.tags, [])

        tests.clicomm(cmd + "--tags foo --tags +bar --tags baz", bz)
        bug.refresh()
        self.assertEquals(bug.tags, ["foo", "bar", "baz"])

        tests.clicomm(cmd + "--tags=-bar", bz)
        bug.refresh()
        self.assertEquals(bug.tags, ["foo", "baz"])

        bz.update_tags(bug.id, tags_remove=bug.tags)
        bug.refresh()
        self.assertEquals(bug.tags, [])
