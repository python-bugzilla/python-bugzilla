#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests that do permanent functional against a real bugzilla instances.
"""

from __future__ import print_function

import datetime
import os
import random
import sys
import unittest

# pylint: disable=import-error
if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO
# pylint: enable=import-error

import pytest

import bugzilla
from bugzilla import Bugzilla
import tests


RHURL = tests.CLICONFIG.REDHAT_URL or "partner-bugzilla.redhat.com"


def _split_int(s):
    return [int(i) for i in s.split(",")]


if not bugzilla.RHBugzilla(url=RHURL).logged_in:
    print("R/W tests require cached login credentials for url=%s" % RHURL)
    sys.exit(1)


class RHPartnerTest(unittest.TestCase):
    # Despite its name, this instance is simply for bugzilla testing,
    # doesn't send out emails and is blown away occasionally. The front
    # page has some info.
    url = RHURL
    bzclass = bugzilla.RHBugzilla

    def _check_have_admin(self, bz, funcname):
        # groupnames is empty for any user if our logged in user does not
        # have admin privs.
        # Check a known account that likely won't ever go away
        ret = bool(bz.getuser("anaconda-maint-list@redhat.com").groupnames)
        if not ret:
            print("\nNo admin privs, reduced testing of %s" % funcname)
        return ret

    def test0LoggedInNoCreds(self):
        bz = self.bzclass(url=self.url, use_creds=False)
        assert not bz.logged_in

    def test2(self):
        bz = Bugzilla(url=self.url, use_creds=False)
        assert bz.__class__ is self.bzclass

    def _makebug(self, bz):
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

        assert len(newout.splitlines()) == 3
        bugid = int(newout.splitlines()[2])
        bug = bz.getbug(bugid)
        print("\nCreated bugid: %s" % bug.id)

        assert bug.component == component
        assert bug.version == version
        assert bug.summary == summary

        return bug

    def test03NewBugBasic(self):
        """
        Create a bug with minimal amount of fields, then close it
        """
        bz = self.bzclass(url=self.url)
        bug = self._makebug(bz)

        # Verify hasattr works
        assert hasattr(bug, "id")
        assert hasattr(bug, "bug_id")

        # Close the bug
        tests.clicomm("bugzilla modify --close NOTABUG %s" % bug.id, bz)
        bug.refresh()
        assert bug.status == "CLOSED"
        assert bug.resolution == "NOTABUG"


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

        assert len(newout.splitlines()) == 3

        bugid = int(newout.splitlines()[2])
        bug = bz.getbug(bugid, extra_fields=["sub_components"])
        print("\nCreated bugid: %s" % bugid)

        assert bug.summary == summary
        assert bug.bug_file_loc == url
        assert bug.op_sys == osval
        assert bug.blocks == _split_int(blocked)
        assert bug.depends_on == _split_int(dependson)
        assert all([e in bug.cc for e in cc.split(",")])
        assert bug.longdescs[0]["text"] == comment
        assert bug.sub_components == {"lvm2": [sub_component]}
        assert bug.alias == [alias]

        # Close the bug

        # RHBZ makes it difficult to provide consistent semantics for
        # 'alias' update:
        # https://bugzilla.redhat.com/show_bug.cgi?id=1173114
        # alias += "-closed"
        tests.clicomm("bugzilla modify "
            "--close WONTFIX %s " %
            bugid, bz)
        bug.refresh()
        assert bug.status == "CLOSED"
        assert bug.resolution == "WONTFIX"
        assert bug.alias == [alias]

        # Check bug's minimal history
        ret = bug.get_history_raw()
        assert len(ret["bugs"]) == 1
        assert len(ret["bugs"][0]["history"]) == 1


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
            assert bug.status == "ASSIGNED"

        origstatus = bug.status

        # Set to ON_QA with a private comment
        status = "ON_QA"
        comment = ("changing status to %s at %s" %
                   (status, datetime.datetime.today()))
        tests.clicomm(cmd +
            "--status %s --comment \"%s\" --private" % (status, comment), bz)

        bug.refresh()
        assert bug.status == status
        assert bug.longdescs[-1]["is_private"] == 1
        assert bug.longdescs[-1]["text"] == comment

        # Close bug as DEFERRED with a private comment
        resolution = "DEFERRED"
        comment = ("changing status to CLOSED=%s at %s" %
                   (resolution, datetime.datetime.today()))
        tests.clicomm(cmd +
            "--close %s --comment \"%s\" --private" %
            (resolution, comment), bz)

        bug.refresh()
        assert bug.status == "CLOSED"
        assert bug.resolution == resolution
        assert bug.comments[-1]["is_private"] == 1
        assert bug.comments[-1]["text"] == comment

        # Close bug as dup with no comment
        dupeid = "461686"
        desclen = len(bug.longdescs)
        tests.clicomm(cmd +
            "--close DUPLICATE --dupeid %s" % dupeid, bz)

        bug.refresh()
        assert bug.dupe_of == int(dupeid)
        assert len(bug.longdescs) == (desclen + 1)
        assert "marked as a duplicate" in bug.longdescs[-1]["text"]

        # bz.setstatus test
        comment = ("adding lone comment at %s" % datetime.datetime.today())
        bug.setstatus("POST", comment=comment, private=True)
        bug.refresh()
        assert bug.longdescs[-1]["is_private"] == 1
        assert bug.longdescs[-1]["text"] == comment
        assert bug.status == "POST"

        # bz.close test
        fixed_in = str(datetime.datetime.today())
        bug.close("ERRATA", fixedin=fixed_in)
        bug.refresh()
        assert bug.status == "CLOSED"
        assert bug.resolution == "ERRATA"
        assert bug.fixed_in == fixed_in

        # bz.addcomment test
        comment = ("yet another test comment %s" % datetime.datetime.today())
        bug.addcomment(comment, private=False)
        bug.refresh()
        assert bug.longdescs[-1]["text"] == comment
        assert bug.longdescs[-1]["is_private"] == 0

        # Confirm comments is same as getcomments
        assert bug.comments == bug.getcomments()

        # Reset state
        tests.clicomm(cmd + "--status %s" % origstatus, bz)
        bug.refresh()
        assert bug.status == origstatus


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
        assert email1 in bug.cc
        assert email2 in bug.cc
        assert len(bug.cc) == 2

        tests.clicomm(cmd + "--cc=-%s" % email1, bz)
        bug.refresh()
        assert email1 not in bug.cc

        # Test assigned target
        tests.clicomm(cmd + "--assignee %s" % email1, bz)
        bug.refresh()
        assert bug.assigned_to == email1

        # Test QA target
        tests.clicomm(cmd + "--qa_contact %s" % email1, bz)
        bug.refresh()
        assert bug.qa_contact == email1

        # Reset values
        bug.deletecc(bug.cc)
        tests.clicomm(cmd + "--reset-qa-contact --reset-assignee", bz)

        bug.refresh()
        assert bug.cc == []
        assert bug.assigned_to == "crobinso@redhat.com"
        assert bug.qa_contact == "extras-qa@fedoraproject.org"


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

        def cleardict_old(b):
            """
            Clear flag dictionary, for format meant for bug.updateflags
            """
            clearflags = {}
            for flag in b.flags:
                clearflags[flag["name"]] = "X"
            return clearflags

        def cleardict_new(b):
            """
            Clear flag dictionary, for format meant for update_bugs
            """
            clearflags = []
            for flag in b.flags:
                clearflags.append({"name": flag["name"], "status": "X"})
            return clearflags

        bug1 = bz.getbug(bugid1)
        if cleardict_old(bug1):
            bug1.updateflags(cleardict_old(bug1))
        bug2 = bz.getbug(bugid2)
        if cleardict_old(bug2):
            bug2.updateflags(cleardict_old(bug2))


        # Set flags and confirm
        setflags = "needinfo? requires_doc_text-"
        tests.clicomm(cmd +
            " ".join([(" --flag " + f) for f in setflags.split()]), bz)

        bug1.refresh()
        bug2.refresh()

        assert flagstr(bug1) == setflags
        assert flagstr(bug2) == setflags
        assert bug1.get_flags("needinfo")[0]["status"] == "?"
        assert bug1.get_flag_status("requires_doc_text") == "-"

        # Clear flags
        if cleardict_new(bug1):
            bz.update_flags(bug1.id, cleardict_new(bug1))
        bug1.refresh()
        if cleardict_new(bug2):
            bz.update_flags(bug2.id, cleardict_new(bug2))
        bug2.refresh()

        assert cleardict_old(bug1) == {}
        assert cleardict_old(bug2) == {}

        # Set "Fixed In" field
        origfix1 = bug1.fixed_in
        origfix2 = bug2.fixed_in

        newfix = origfix1 and (origfix1 + "-new1") or "blippy1"
        if newfix == origfix2:
            newfix = origfix2 + "-2"

        tests.clicomm(cmd + "--fixed_in=%s" % newfix, bz)

        bug1.refresh()
        bug2.refresh()
        assert bug1.fixed_in == newfix
        assert bug2.fixed_in == newfix

        # Reset fixed_in
        tests.clicomm(cmd + "--fixed_in=\"-\"", bz)

        bug1.refresh()
        bug2.refresh()
        assert bug1.fixed_in == "-"
        assert bug2.fixed_in == "-"


    def test07ModifyMisc(self):
        bugid = "461686"
        cmd = "bugzilla modify %s " % bugid
        bz = self.bzclass(url=self.url)
        bug = bz.getbug(bugid)

        # modify --dependson
        tests.clicomm(cmd + "--dependson 123456", bz)
        bug.refresh()
        assert 123456 in bug.depends_on
        tests.clicomm(cmd + "--dependson =111222", bz)
        bug.refresh()
        assert [111222] == bug.depends_on
        tests.clicomm(cmd + "--dependson=-111222", bz)
        bug.refresh()
        assert [] == bug.depends_on

        # modify --blocked
        tests.clicomm(cmd + "--blocked 123,456", bz)
        bug.refresh()
        assert [123, 456] == bug.blocks
        tests.clicomm(cmd + "--blocked =", bz)
        bug.refresh()
        assert [] == bug.blocks

        # modify --keywords
        tests.clicomm(cmd + "--keywords +Documentation --keywords EasyFix", bz)
        bug.refresh()
        assert ["Documentation", "EasyFix"] == bug.keywords
        tests.clicomm(cmd + "--keywords=-EasyFix --keywords=-Documentation",
                      bz)
        bug.refresh()
        assert [] == bug.keywords

        # modify --target_release
        # modify --target_milestone
        targetbugid = 492463
        targetbug = bz.getbug(targetbugid)
        targetcmd = "bugzilla modify %s " % targetbugid
        tests.clicomm(targetcmd +
                      "--target_milestone beta --target_release 6.2", bz)
        targetbug.refresh()
        assert targetbug.target_milestone == "beta"
        assert targetbug.target_release == ["6.2"]
        tests.clicomm(targetcmd +
                      "--target_milestone rc --target_release 6.10", bz)
        targetbug.refresh()
        assert targetbug.target_milestone == "rc"
        assert targetbug.target_release == ["6.10"]

        # modify --priority
        # modify --severity
        tests.clicomm(cmd + "--priority low --severity high", bz)
        bug.refresh()
        assert bug.priority == "low"
        assert bug.severity == "high"
        tests.clicomm(cmd + "--priority medium --severity medium", bz)
        bug.refresh()
        assert bug.priority == "medium"
        assert bug.severity == "medium"

        # modify --os
        # modify --platform
        # modify --version
        tests.clicomm(cmd + "--version rawhide --os Windows --arch ppc "
                            "--url http://example.com", bz)
        bug.refresh()
        assert bug.version == "rawhide"
        assert bug.op_sys == "Windows"
        assert bug.platform == "ppc"
        assert bug.url == "http://example.com"
        tests.clicomm(cmd + "--version rawhide --os Linux --arch s390 "
                            "--url http://example.com/fribby", bz)
        bug.refresh()
        assert bug.version == "rawhide"
        assert bug.op_sys == "Linux"
        assert bug.platform == "s390"
        assert bug.url == "http://example.com/fribby"

        # modify --field
        tests.clicomm(cmd + "--field cf_fixed_in=foo-bar-1.2.3 \
                      --field=cf_release_notes=baz", bz)

        bug.refresh()
        assert bug.fixed_in == "foo-bar-1.2.3"
        assert bug.cf_release_notes == "baz"


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
        cmd = "bugzilla attach "
        testfile = "../tests/data/bz-attach-get1.txt"

        # Add attachment as CLI option
        setbug = self._makebug(bz)
        setbug = bz.getbug(setbug.id, extra_fields=["attachments"])
        orignumattach = len(setbug.attachments)

        # Add attachment from CLI with mime guessing
        desc1 = "python-bugzilla cli upload %s" % datetime.datetime.today()
        out1 = tests.clicomm(cmd + "%s --description \"%s\" --file %s" %
                             (setbug.id, desc1, testfile), bz,
                             stdin=open("/dev/tty", "rb"))

        desc2 = "python-bugzilla cli upload %s" % datetime.datetime.today()
        out2 = tests.clicomm(cmd + "%s --file test --summary \"%s\"" %
                             (setbug.id, desc2), bz, stdin=open(testfile))

        # Expected output format:
        #   Created attachment <attachid> on bug <bugid>

        setbug.refresh()
        assert len(setbug.attachments) == (orignumattach + 2)

        att1 = setbug.attachments[-2]
        attachid = att1["id"]
        assert att1["summary"] == desc1
        assert att1["id"] == int(out1.splitlines()[2].split()[2])
        assert att1["content_type"] == "text/plain"

        att2 = setbug.attachments[-1]
        assert att2["summary"] == desc2
        assert att2["id"] == int(out2.splitlines()[2].split()[2])
        assert att2["content_type"] == "application/octet-stream"

        # Set attachment flags
        assert att1["flags"] == []
        bz.updateattachmentflags(setbug.id, att2["id"], "review", status="+")
        setbug.refresh()

        assert len(setbug.attachments[-1]["flags"]) == 1
        assert setbug.attachments[-1]["flags"][0]["name"] == "review"
        assert setbug.attachments[-1]["flags"][0]["status"] == "+"

        bz.updateattachmentflags(setbug.id, setbug.attachments[-1]["id"],
                                 "review", status="X")
        setbug.refresh()
        assert setbug.attachments[-1]["flags"] == []


        # Get attachment, verify content
        out = tests.clicomm(cmd + "--get %s" % attachid, bz).splitlines()

        # Expect format:
        #   Wrote <filename>
        fname = out[2].split()[1].strip()

        assert len(out) == 3
        assert fname == "bz-attach-get1.txt"
        assert open(fname).read() == open(testfile).read()
        os.unlink(fname)

        # Get all attachments
        getbug = bz.getbug(setbug.id)
        getbug.autorefresh = True
        numattach = len(getbug.attachments)
        out = tests.clicomm(cmd + "--getall %s" % getbug.id, bz).splitlines()

        assert len(out) == (numattach + 2)
        fnames = [l.split(" ", 1)[1].strip() for l in out[2:]]
        assert len(fnames) == numattach
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
        assert bug.whiteboard == (initval + "status")
        assert bug.qa_whiteboard == (initval + "qa")
        assert bug.devel_whiteboard == (initval + "devel")
        assert (bug.internal_whiteboard ==
                (initval + "internal, security, foo security1"))

        # Modify whiteboards
        tests.clicomm(cmd +
                      "--whiteboard =foobar "
                      "--qa_whiteboard _app "
                      "--devel_whiteboard =pre-%s" % bug.devel_whiteboard, bz)

        bug.refresh()
        assert bug.qa_whiteboard == (initval + "qa" + " _app")
        assert bug.devel_whiteboard == ("pre-" + initval + "devel")
        assert bug.status_whiteboard == "foobar"

        # Verify that tag manipulation is smart about separator
        tests.clicomm(cmd +
                      "--qa_whiteboard=-_app "
                      "--internal_whiteboard=-security,", bz)
        bug.refresh()

        assert bug.qa_whiteboard == (initval + "qa")
        assert bug.internal_whiteboard == (initval + "internal, foo security1")

        # Clear whiteboards
        update = bz.build_update(
            whiteboard="", devel_whiteboard="",
            internal_whiteboard="", qa_whiteboard="")
        bz.update_bugs(bug.id, update)

        bug.refresh()
        assert bug.whiteboard == ""
        assert bug.qa_whiteboard == ""
        assert bug.devel_whiteboard == ""
        assert bug.internal_whiteboard == ""


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
            cmd = "bugzilla --no-cache-credentials --bugzilla %s" % self.url
            # Implied login with --username and --password
            ret = tests.clicomm("%s --user foobar@example.com "
                                "--password foobar query -b 123456" % cmd,
                                None, expectfail=True)
            assert "Login failed: " in ret

            # 'login' with explicit options
            ret = tests.clicomm("%s --user foobar@example.com "
                                "--password foobar login" % cmd,
                                None, expectfail=True)
            assert "Login failed: " in ret

            # 'login' with positional options
            ret = tests.clicomm("%s login foobar@example.com foobar" % cmd,
                                None, expectfail=True)
            assert "Login failed: " in ret


            # bare 'login'
            stdinstr = StringIO("foobar@example.com\n\rfoobar\n\r")
            ret = tests.clicomm("%s login" % cmd,
                                None, expectfail=True, stdin=stdinstr)
            assert "Bugzilla Username:" in ret
            assert "Bugzilla Password:" in ret
            assert "Login failed: " in ret
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
            assert group in user.groupnames
        origgroups = user.groupnames

        # Remove the group
        try:
            bz.updateperms(email, "remove", [group])
            user.refresh()
            assert group not in user.groupnames
        except Exception as e:
            if have_admin:
                raise
            assert "Sorry, you aren't a member" in str(e)

        # Re add it
        try:
            bz.updateperms(email, "add", group)
            user.refresh()
            assert group in user.groupnames
        except Exception as e:
            if have_admin:
                raise
            assert "Sorry, you aren't a member" in str(e)

        # Set groups
        try:
            newgroups = user.groupnames[:]
            if have_admin:
                newgroups.remove(group)
            bz.updateperms(email, "set", newgroups)
            user.refresh()
            assert group not in user.groupnames
        except Exception as e:
            if have_admin:
                raise
            assert "Sorry, you aren't a member" in str(e)

        # Reset everything
        try:
            bz.updateperms(email, "set", origgroups)
        except Exception as e:
            if have_admin:
                raise
            assert "Sorry, you aren't a member" in str(e)

        user.refresh()
        assert user.groupnames == origgroups


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

            assert bool(compdata)
            assert data["component"] == compdata["name"]
            assert data["description"] == compdata["description"]
            assert data["initialowner"] == compdata["default_assigned_to"]
            assert data["initialqacontact"] == compdata["default_qa_contact"]
            assert data["is_active"] == compdata["is_active"]


        # Create component
        data = basedata.copy()
        data.update({
            "description": "foo test bar",
            "initialowner": "crobinso@redhat.com",
            "initialqacontact": "extras-qa@fedoraproject.org",
            "initialcclist": ["wwoods@redhat.com", "toshio@fedoraproject.org"],
            "is_active": True,
        })
        newid = None
        try:
            newid = bz.addcomponent(data)['id']
            print("Created product=%s component=%s" % (
                basedata["product"], basedata["component"]))
            compare(data, newid)
        except Exception as e:
            if have_admin:
                raise
            assert (("Sorry, you aren't a member" in str(e)) or
                # bugzilla 5 error string
                ("You are not allowed" in str(e)))


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
            if newid is not None:
                compare(data, newid)
        except Exception as e:
            if have_admin:
                raise
            assert (("Sorry, you aren't a member" in str(e)) or
                # bugzilla 5 error string
                ("You are not allowed" in str(e)))

    def test12SetCookie(self):
        bz = self.bzclass(self.url,
                cookiefile=-1, tokenfile=None, configpaths=[])

        try:
            bz.cookiefile = None
            raise AssertionError("Setting cookiefile for active connection "
                                 "should fail.")
        except RuntimeError as e:
            assert "disconnect()" in str(e)

        bz.disconnect()
        bz.cookiefile = None
        bz.connect()
        assert not bz.logged_in

    def test13SubComponents(self):
        bz = self.bzclass(url=self.url)
        # Long closed RHEL5 lvm2 bug. This component has sub_components
        bug = bz.getbug("185526")
        bug.autorefresh = True
        assert bug.component == "lvm2"

        bz.update_bugs(bug.id, bz.build_update(
            component="lvm2", sub_component="Command-line tools (RHEL5)"))
        bug.refresh()
        assert bug.sub_components == {"lvm2": ["Command-line tools (RHEL5)"]}

        bz.update_bugs(bug.id, bz.build_update(sub_component={}))
        bug.refresh()
        assert bug.sub_components == {}

    def test13ExternalTrackerQuery(self):
        bz = self.bzclass(url=self.url)
        with pytest.raises(RuntimeError):
            bz.build_external_tracker_boolean_query()

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
            assert bug.tags == []

        tests.clicomm(cmd + "--tags foo --tags +bar --tags baz", bz)
        bug.refresh()
        assert bug.tags, ["foo", "bar" == "baz"]

        tests.clicomm(cmd + "--tags=-bar", bz)
        bug.refresh()
        assert bug.tags, ["foo" == "baz"]

        bz.update_tags(bug.id, tags_remove=bug.tags)
        bug.refresh()
        assert bug.tags == []

    def test17LoginAPIKey(self):
        api_key = "somefakeapikey1234"
        bz = self.bzclass(url=self.url, use_creds=False, api_key=api_key)
        if bz.bz_ver_major < 5:
            self.skipTest("can only test apikey on bugzilla 5+")

        try:
            assert bz.logged_in is False

            # Use this to trigger a warning about api_key
            bz.createbug(bz.build_createbug())
        except Exception as e:
            assert "The API key you specified is invalid" in str(e)
