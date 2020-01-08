# -*- encoding: utf-8 -*-

#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests that do readonly functional tests against real bugzilla instances.
"""

import os

import bugzilla
import tests


REDHAT_URL = (tests.CLICONFIG.REDHAT_URL or
    "https://bugzilla.redhat.com")


def _open_bz(url, **kwargs):
    if "use_creds" not in kwargs:
        kwargs["use_creds"] = False
    return bugzilla.Bugzilla(url, **kwargs)


def _check(out, mincount, expectstr):
    # Since we are running these tests against bugzilla instances in
    # the wild, we can't depend on certain data like product lists
    # remaining static. Use lax sanity checks in this case
    if mincount is not None:
        assert len(out.splitlines()) >= mincount
    assert expectstr in out


def _test_version(bz, bzversion):
    assert bz.bz_ver_major == bzversion[0]
    assert bz.bz_ver_minor == bzversion[1]


###################
# mozilla testing #
###################

def test_mozilla():
    url = "bugzilla.mozilla.org"
    bz = _open_bz(url)

    # bugzilla.mozilla.org returns version values in YYYY-MM-DD
    # format, so just try to confirm that
    assert bz.__class__ == bugzilla.Bugzilla
    assert bz.bz_ver_major >= 2016
    assert bz.bz_ver_minor in range(1, 13)


##################
# gentoo testing #
##################

def test_gentoo():
    url = "bugs.gentoo.org"
    bzversion = (5, 0)
    bz = _open_bz(url)
    _test_version(bz, bzversion)

    # This is a bugzilla 5.0 instance, which supports URL queries now
    query_url = ("https://bugs.gentoo.org/buglist.cgi?"
        "component=[CS]&product=Doc%20Translations"
        "&query_format=advanced&resolution=FIXED")
    ret = bz.query(bz.url_to_query(query_url))
    assert len(ret) > 0


##################
# redhat testing #
##################


def testInfoProducts(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli("bugzilla info --products", bz)
    _check(out, 123, "Virtualization Tools")


def testInfoComps(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli("bugzilla info --components 'Virtualization Tools'", bz)
    _check(out, 8, "virtinst")


def testInfoVers(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli("bugzilla info --versions Fedora", bz)
    _check(out, 17, "rawhide")


def testInfoCompOwners(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli("bugzilla info "
            "--component_owners 'Virtualization Tools'", bz)
    _check(out, None, "libvirt: Libvirt Maintainers")


def testQuery(run_cli):
    bz = _open_bz(REDHAT_URL)

    args = "--product Fedora --component python-bugzilla --version 14"
    cli = "bugzilla query %s --bug_status CLOSED" % args
    mincount = 4
    expectbug = "621030"
    out = run_cli(cli, bz)

    assert len(out.splitlines()) >= mincount
    assert bool([l1 for l1 in out.splitlines() if
                 l1.startswith("#" + expectbug)])

    # Check --ids output option
    out2 = run_cli(cli + " --ids", bz)
    assert len(out.splitlines()) == len(out2.splitlines())
    assert bool([l2 for l2 in out2.splitlines() if
                 l2 == expectbug])


def testQueryFull(run_cli):
    bz = _open_bz(REDHAT_URL)

    bugid = "621601"
    out = run_cli("bugzilla query --full --bug_id %s" % bugid, bz)
    _check(out, 60, "end-of-life (EOL)")


def testQueryRaw(run_cli):
    bz = _open_bz(REDHAT_URL)

    bugid = "307471"
    out = run_cli("bugzilla query --raw --bug_id %s" % bugid, bz)
    _check(out, 70, "ATTRIBUTE[whiteboard]:  bzcl34nup")


def testQueryOneline(run_cli):
    bz = _open_bz(REDHAT_URL)

    bugid = "785016"
    out = run_cli("bugzilla query --oneline --bug_id %s" % bugid, bz)
    assert len(out.splitlines()) == 1
    assert out.splitlines()[0].startswith("#%s" % bugid)
    assert "[---] fedora-review+,fedora-cvs+" in out

    bugid = "720784"
    out = run_cli("bugzilla query --oneline --bug_id %s" % bugid, bz)
    assert len(out.splitlines()) == 1
    assert out.splitlines()[0].startswith("#%s" % bugid)
    assert " CVE-2011-2527" in out


def testQueryExtra(run_cli):
    bz = _open_bz(REDHAT_URL)

    bugid = "307471"
    out = run_cli("bugzilla query --extra --bug_id %s" % bugid, bz)
    assert ("#%s" % bugid) in out
    assert " +Status Whiteboard:  bzcl34nup" in out


def testQueryFormat(run_cli):
    bz = _open_bz(REDHAT_URL)

    args = ("--bug_id 307471 --outputformat=\"id=%{bug_id} "
        "sw=%{whiteboard:status} needinfo=%{flag:needinfo} "
        "sum=%{summary}\"")
    out = run_cli("bugzilla query %s" % args, bz)
    assert "id=307471 sw= bzcl34nup needinfo= " in out

    args = ("--bug_id 785016 --outputformat=\"id=%{bug_id} "
        "sw=%{whiteboard:status} flag=%{flag:fedora-review} "
        "sum=%{summary}\"")
    out = run_cli("bugzilla query %s" % args, bz)
    assert "id=785016 sw= flag=+" in out

    # Unicode in this bug's summary
    args = "--bug_id 522796 --outputformat \"%{summary}\""
    out = run_cli("bugzilla query %s" % args, bz)
    assert "V34 — system" in out


def testQueryURL(run_cli):
    bz = _open_bz(REDHAT_URL)

    qurl = ("/buglist.cgi?f1=creation_ts"
        "&list_id=973582&o1=greaterthaneq&classification=Fedora&"
        "o2=lessthaneq&query_format=advanced&f2=creation_ts"
        "&v1=2010-01-01&component=python-bugzilla&v2=2011-01-01"
        "&product=Fedora")

    url = REDHAT_URL
    if "/xmlrpc.cgi" in url:
        url = url.replace("/xmlrpc.cgi", qurl)
    else:
        url += qurl
    out = run_cli("bugzilla query --from-url \"%s\"" % url, bz)
    _check(out, 22, "#553878 CLOSED")


def testDoubleConnect():
    bz = _open_bz(REDHAT_URL)
    bz.connect(REDHAT_URL)


def testQueryFlags(run_cli):
    bz = _open_bz(REDHAT_URL)

    if not bz.logged_in:
        print("not logged in, skipping testQueryFlags")
        return

    out = run_cli("bugzilla query --product 'Red Hat Enterprise Linux 5' "
        "--component virt-manager --bug_status CLOSED "
        "--flag rhel-5.4.0+", bz)
    assert len(out.splitlines()) > 13
    assert len(out.splitlines()) < 26
    assert "223805" in out


def testQueryFixedIn(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli("bugzilla query --fixed_in anaconda-15.29-1", bz)
    assert len(out.splitlines()) == 4
    assert "#629311 CLOSED" in out


def testComponentsDetails():
    """
    Fresh call to getcomponentsdetails should properly refresh
    """
    bz = _open_bz(REDHAT_URL)

    assert bool(bz.getcomponentsdetails("Red Hat Developer Toolset"))


def testGetBugAlias():
    """
    getbug() works if passed an alias
    """
    bz = _open_bz(REDHAT_URL)

    bug = bz.getbug("CVE-2011-2527")
    assert bug.bug_id == 720773


def testQuerySubComponent(run_cli):
    bz = _open_bz(REDHAT_URL)

    # Test special error wrappers in bugzilla/_cli.py
    out = run_cli("bugzilla query --product 'Red Hat Enterprise Linux 7' "
        "--component lvm2 --sub-component 'Thin Provisioning'", bz)
    assert len(out.splitlines()) >= 3
    assert "#1060931 " in out


def testBugFields():
    bz = _open_bz(REDHAT_URL)
    fields = bz.getbugfields(names=["product"])[:]
    assert fields == ["product"]
    bz.getbugfields(names=["product", "bug_status"], force_refresh=True)
    assert set(bz.bugfields) == set(["product", "bug_status"])


def testBugAutoRefresh():
    bz = _open_bz(REDHAT_URL)

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


def testExtraFields():
    bz = _open_bz(REDHAT_URL)

    # Check default extra_fields will pull in comments
    bug = bz.getbug(720773, exclude_fields=["product"])
    assert "comments" in dir(bug)
    assert "product" not in dir(bug)

    # Ensure that include_fields overrides default extra_fields
    bug = bz.getbug(720773, include_fields=["summary"])
    assert "summary" in dir(bug)
    assert "comments" not in dir(bug)


def testExternalBugsOutput(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli('bugzilla query --bug_id 989253 '
        '--outputformat="%{external_bugs}"', bz)
    assert "bugzilla.gnome.org/show_bug.cgi?id=703421" in out
    assert "External bug: https://bugs.launchpad.net/bugs/1203576" in out


def testActiveComps(run_cli):
    bz = _open_bz(REDHAT_URL)

    out = run_cli("bugzilla info --components 'Virtualization Tools' "
            "--active-components", bz)
    assert "virtinst" not in out
    out = run_cli("bugzilla info --component_owners 'Virtualization Tools' "
            "--active-components", bz)
    assert "virtinst" not in out


def testFaults(run_cli):
    bz = _open_bz(REDHAT_URL)

    # Test special error wrappers in bugzilla/_cli.py
    out = run_cli("bugzilla query --field=IDONTEXIST=FOO", bz,
            expectfail=True)
    assert "Server error:" in out

    out = run_cli("bugzilla "
        "--bugzilla https://example.com/xmlrpc.cgi "
        "query --field=IDONTEXIST=FOO", None, expectfail=True)
    assert "Connection lost/failed" in out

    out = run_cli("bugzilla "
        "--bugzilla https://expired.badssl.com/ "
        "query --bug_id 1234", None, expectfail=True)
    assert "trust the remote server" in out
    assert "--nosslverify" in out


def testCertFail(run_cli):
    # No public setup that I know of to test cert succeeds, so
    # let's give it a bogus file and ensure it fails
    badcert = os.path.join(os.path.dirname(__file__), "..", "README.md")
    out = run_cli(
        "bugzilla --cert %s query --bug_id 123456" % badcert,
        None, expectfail=True)
    assert "PEM" in out


def test_redhat():
    bzversion = (5, 0)
    bz = _open_bz(REDHAT_URL)

    if not tests.CLICONFIG.REDHAT_URL:
        _test_version(bz, bzversion)
