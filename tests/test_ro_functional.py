# -*- encoding: utf-8 -*-

#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests that do readonly functional tests against real bugzilla instances.
"""

import os
import unittest

import pytest

from bugzilla import Bugzilla, BugzillaError, RHBugzilla
import tests


class BaseTest(unittest.TestCase):
    url = None
    bzclass = Bugzilla
    bzversion = (0, 0)
    closestatus = "CLOSED"

    def clicomm(self, argstr, expectexc=False, bz=None):
        comm = "bugzilla " + argstr

        if not bz:
            bz = Bugzilla(url=self.url, use_creds=False)
        if expectexc:
            with pytest.raises(Exception):
                tests.clicomm(comm, bz)
        else:
            return tests.clicomm(comm, bz)

    def _testBZVersion(self):
        bz = Bugzilla(self.url, use_creds=False)
        assert bz.__class__ == self.bzclass
        if tests.CLICONFIG.REDHAT_URL:
            return
        assert bz.bz_ver_major == self.bzversion[0]
        assert bz.bz_ver_minor == self.bzversion[1]

    # Since we are running these tests against bugzilla instances in
    # the wild, we can't depend on certain data like product lists
    # remaining static. Use lax sanity checks in this case

    def _testInfoProducts(self, mincount, expectstr):
        out = self.clicomm("info --products").splitlines()
        assert len(out) >= mincount
        assert expectstr in out

    def _testInfoComps(self, comp, mincount, expectstr):
        out = self.clicomm("info --components \"%s\"" % comp).splitlines()
        assert len(out) >= mincount
        assert expectstr in out

    def _testInfoVers(self, comp, mincount, expectstr):
        out = self.clicomm("info --versions \"%s\"" % comp).splitlines()
        assert len(out) >= mincount
        if expectstr:
            assert expectstr in out

    def _testInfoCompOwners(self, comp, expectstr):
        expectexc = (expectstr == "FAIL")
        out = self.clicomm("info --component_owners \"%s\"" %
                           comp, expectexc=expectexc)
        if expectexc:
            return

        assert expectstr in out.splitlines()

    def _testQuery(self, args, mincount, expectbug):
        expectexc = (expectbug == "FAIL")
        cli = "query %s --bug_status %s" % (args, self.closestatus)
        out = self.clicomm(cli, expectexc=expectexc)
        if expectexc:
            return

        assert len(out.splitlines()) >= mincount
        assert bool([l1 for l1 in out.splitlines() if
                     l1.startswith("#" + expectbug)])

        # Check --ids output option
        out2 = self.clicomm(cli + " --ids")
        assert len(out.splitlines()) == len(out2.splitlines())
        assert bool([l2 for l2 in out2.splitlines() if
                     l2 == expectbug])


    def _testQueryFull(self, bugid, mincount, expectstr):
        out = self.clicomm("query --full --bug_id %s" % bugid)
        assert len(out.splitlines()) >= mincount
        assert expectstr in out

    def _testQueryRaw(self, bugid, mincount, expectstr):
        out = self.clicomm("query --raw --bug_id %s" % bugid)
        assert len(out.splitlines()) >= mincount
        assert expectstr in out

    def _testQueryOneline(self, bugid, expectstr):
        out = self.clicomm("query --oneline --bug_id %s" % bugid)
        assert len(out.splitlines()) == 3
        assert out.splitlines()[2].startswith("#%s" % bugid)
        assert expectstr in out

    def _testQueryExtra(self, bugid, expectstr):
        out = self.clicomm("query --extra --bug_id %s" % bugid)
        assert ("#%s" % bugid) in out
        assert expectstr in out

    def _testQueryFormat(self, args, expectstr):
        out = self.clicomm("query %s" % args)
        assert expectstr in out

    def _testQueryURL(self, querystr, count, expectstr):
        url = self.url
        if "/xmlrpc.cgi" in self.url:
            url = url.replace("/xmlrpc.cgi", querystr)
        else:
            url += querystr
        out = self.clicomm("query --from-url \"%s\"" % url)
        assert len(out.splitlines()) == count
        assert expectstr in out


class BZMozilla(BaseTest):
    def testVersion(self):
        # bugzilla.mozilla.org returns version values in YYYY-MM-DD
        # format, so just try to confirm that
        try:
            bz = Bugzilla("bugzilla.mozilla.org", use_creds=False)
            assert bz.__class__ == Bugzilla
            assert bz.bz_ver_major >= 2016
            assert bz.bz_ver_minor in range(1, 13)
        except Exception as e:
            # travis environment throws SSL errors here
            # https://travis-ci.org/python-bugzilla/python-bugzilla/builds/304713566
            if "EOF occurred" not in str(e):
                raise
            self.skipTest("travis environment SSL error hit: %s" % str(e))


class BZGentoo(BaseTest):
    url = "bugs.gentoo.org"
    bzversion = (5, 0)
    test0 = BaseTest._testBZVersion

    def testURLQuery(self):
        # This is a bugzilla 5.0 instance, which supports URL queries now
        query_url = ("https://bugs.gentoo.org/buglist.cgi?"
            "component=[CS]&product=Doc%20Translations"
            "&query_format=advanced&resolution=FIXED")
        bz = Bugzilla(url=self.url, use_creds=False)
        ret = bz.query(bz.url_to_query(query_url))
        assert len(ret) > 0


class BZGnome(BaseTest):
    url = "https://bugzilla.gnome.org/xmlrpc.cgi"
    bzversion = (4, 4)
    closestatus = "RESOLVED"

    test0 = BaseTest._testBZVersion
    test1 = lambda s: BaseTest._testQuery(s,
                "--product dogtail --component sniff",
                9, "321654")
    # BZ < 4 doesn't report values for --full
    test2 = lambda s: BaseTest._testQueryRaw(s, "321654", 30,
                                             "ATTRIBUTE[version]: CVS HEAD")
    test3 = lambda s: BaseTest._testQueryOneline(s, "321654", "Sniff")

    def testURLQuery(self):
        # This instance is old and doesn't support URL queries, we are
        # just verifying our extra error message report
        query_url = ("https://bugzilla.gnome.org/buglist.cgi?"
            "bug_status=RESOLVED&order=Importance&product=accerciser"
            "&query_format=advanced&resolution=NOTABUG")
        bz = Bugzilla(url=self.url, use_creds=False)
        try:
            bz.query(bz.url_to_query(query_url))
        except BugzillaError as e:
            assert "derived from bugzilla" in str(e)


class BZFDO(BaseTest):
    url = "https://bugs.freedesktop.org/xmlrpc.cgi"
    bzversion = (5, 0)
    closestatus = "CLOSED,RESOLVED"

    test0 = BaseTest._testBZVersion

    test1 = lambda s: BaseTest._testQuery(s, "--product avahi", 10, "3450")
    test2 = lambda s: BaseTest._testQueryFull(s, "3450", 10, "Blocked: \n")
    test2 = lambda s: BaseTest._testQueryRaw(s, "3450", 30,
                                    "ATTRIBUTE[creator]: daniel@fooishbar.org")
    test3 = lambda s: BaseTest._testQueryOneline(s, "3450",
                                    "daniel@fooishbar.org libavahi")
    test4 = lambda s: BaseTest._testQueryExtra(s, "3450", "Error")
    test5 = lambda s: BaseTest._testQueryFormat(s,
                "--bug_id 3450 --outputformat "
                "\"%{bug_id} %{assigned_to} %{summary}\"",
                "3450 daniel@fooishbar.org Error")


class RHTest(BaseTest):
    url = (tests.CLICONFIG.REDHAT_URL or
        "https://bugzilla.redhat.com/xmlrpc.cgi")
    bzclass = RHBugzilla
    bzversion = (5, 0)

    test0 = BaseTest._testBZVersion
    test01 = lambda s: BaseTest._testInfoProducts(s, 125,
                                                 "Virtualization Tools")
    test02 = lambda s: BaseTest._testInfoComps(s, "Virtualization Tools",
                                              10, "virtinst")
    test03 = lambda s: BaseTest._testInfoVers(s, "Fedora", 19, "rawhide")
    test04 = lambda s: BaseTest._testInfoCompOwners(s, "Virtualization Tools",
                                         "libvirt: Libvirt Maintainers")

    test05 = lambda s: BaseTest._testQuery(s,
                "--product Fedora --component python-bugzilla --version 14",
                6, "621030")
    test06 = lambda s: BaseTest._testQueryFull(s, "621601", 60,
                                              "end-of-life (EOL)")
    test07 = lambda s: BaseTest._testQueryRaw(s, "307471", 70,
                "ATTRIBUTE[whiteboard]:  bzcl34nup")
    test08 = lambda s: BaseTest._testQueryOneline(s, "785016",
                "[---] fedora-review+,fedora-cvs+")
    test09 = lambda s: BaseTest._testQueryExtra(s, "307471",
            " +Status Whiteboard:  bzcl34nup")
    test10 = lambda s: BaseTest._testQueryFormat(s,
            "--bug_id 307471 --outputformat=\"id=%{bug_id} "
            "sw=%{whiteboard:status} needinfo=%{flag:needinfo} "
            "sum=%{summary}\"",
            "id=307471 sw= bzcl34nup needinfo= ")
    test11 = lambda s: BaseTest._testQueryURL(s,
            "/buglist.cgi?f1=creation_ts"
            "&list_id=973582&o1=greaterthaneq&classification=Fedora&"
            "o2=lessthaneq&query_format=advanced&f2=creation_ts"
            "&v1=2010-01-01&component=python-bugzilla&v2=2011-01-01"
            "&product=Fedora", 26, "#553878 CLOSED")
    test12 = lambda s: BaseTest._testQueryFormat(s,
            "--bug_id 785016 --outputformat=\"id=%{bug_id} "
            "sw=%{whiteboard:status} flag=%{flag:fedora-review} "
            "sum=%{summary}\"",
            "id=785016 sw= flag=+")
    # Unicode in this bug's summary
    test13 = lambda s: BaseTest._testQueryFormat(s,
             "--bug_id 522796 --outputformat \"%{summary}\"",
             "V34 — system")
    # CVE bug output
    test14 = lambda s: BaseTest._testQueryOneline(s, "720784",
            " CVE-2011-2527")

    def testDoubleConnect(self):
        bz = self.bzclass(url=self.url)
        bz.connect(self.url)

    def testQueryFlags(self):
        bz = self.bzclass(url=self.url)
        if not bz.logged_in:
            print("not logged in, skipping testQueryFlags")
            return

        out = self.clicomm("query --product 'Red Hat Enterprise Linux 5' "
            "--component virt-manager --bug_status CLOSED "
            "--flag rhel-5.4.0+", bz=bz)
        assert len(out.splitlines()) > 15
        assert len(out.splitlines()) < 28
        assert "223805" in out

    def testQueryFixedIn(self):
        out = self.clicomm("query --fixed_in anaconda-15.29-1")
        assert len(out.splitlines()) == 6
        assert "#629311 CLOSED" in out

    def testComponentsDetails(self):
        """
        Fresh call to getcomponentsdetails should properly refresh
        """
        bz = self.bzclass(url=self.url, use_creds=False)
        assert bool(bz.getcomponentsdetails("Red Hat Developer Toolset"))

    def testGetBugAlias(self):
        """
        getbug() works if passed an alias
        """
        bz = self.bzclass(url=self.url, use_creds=False)
        bug = bz.getbug("CVE-2011-2527")
        assert bug.bug_id == 720773

    def testQuerySubComponent(self):
        out = self.clicomm("query --product 'Red Hat Enterprise Linux 7' "
            "--component lvm2 --sub-component 'Thin Provisioning'")
        assert len(out.splitlines()) >= 5
        assert "#1060931 " in out

    def testBugFields(self):
        bz = self.bzclass(url=self.url, use_creds=False)
        fields1 = bz.getbugfields()[:]
        fields2 = bz.getbugfields(force_refresh=True)[:]
        assert bool([f for f in fields1 if f.startswith("attachments")])
        assert fields1 == fields2

    def testBugAutoRefresh(self):
        bz = self.bzclass(self.url, use_creds=False)

        bz.bug_autorefresh = True

        bug = bz.query(bz.build_query(bug_id=720773,
            include_fields=["summary"]))[0]
        assert hasattr(bug, "component")
        assert bool(bug.component)

        bz.bug_autorefresh = False

        bug = bz.query(bz.build_query(bug_id=720773,
            include_fields=["summary"]))[0]
        assert not hasattr(bug, "component")
        try:
            assert bool(bug.component)
        except Exception as e:
            assert "adjust your include_fields" in str(e)

    def testExtraFields(self):
        bz = self.bzclass(self.url, cookiefile=None, tokenfile=None)

        # Check default extra_fields will pull in comments
        bug = bz.getbug(720773, exclude_fields=["product"])
        assert "comments" in dir(bug)
        assert "product" not in dir(bug)

        # Ensure that include_fields overrides default extra_fields
        bug = bz.getbug(720773, include_fields=["summary"])
        assert "summary" in dir(bug)
        assert "comments" not in dir(bug)

    def testExternalBugsOutput(self):
        out = self.clicomm('query --bug_id 989253 '
            '--outputformat="%{external_bugs}"')
        assert "bugzilla.gnome.org/show_bug.cgi?id=703421" in out
        assert "External bug: https://bugs.launchpad.net/bugs/1203576" in out

    def testActiveComps(self):
        out = self.clicomm("info --components 'Virtualization Tools' "
                "--active-components")
        assert "virtinst" not in out
        out = self.clicomm("info --component_owners 'Virtualization Tools' "
                "--active-components")
        assert "virtinst" not in out

    def testFaults(self):
        # Test special error wrappers in bugzilla/_cli.py
        bzinstance = Bugzilla(self.url, use_creds=False)
        out = tests.clicomm("bugzilla query --field=IDONTEXIST=FOO",
            bzinstance, expectfail=True)
        assert "Server error:" in out

        out = tests.clicomm("bugzilla "
            "--bugzilla https://example.com/xmlrpc.cgi "
            "query --field=IDONTEXIST=FOO", None, expectfail=True)
        assert "Connection lost/failed" in out

        out = tests.clicomm("bugzilla "
            "--bugzilla https://expired.badssl.com/ "
            "query --bug_id 1234", None, expectfail=True)
        assert "trust the remote server" in out
        assert "--nosslverify" in out

    def testCertFail(self):
        # No public setup that I know of to test cert succeeds, so
        # let's give it a bogus file and ensure it fails
        badcert = os.path.join(os.path.dirname(__file__), "..", "README.md")
        out = tests.clicomm(
            "bugzilla --cert %s query --bug_id 123456" % badcert,
            None, expectfail=True)
        assert "PEM" in out
