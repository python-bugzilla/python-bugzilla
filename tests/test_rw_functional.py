#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests that do permanent functional against a real bugzilla instances.
"""

import datetime
import inspect
import os
import random
import sys

import bugzilla

import tests
import tests.mockbackend
import tests.utils


RHURL = tests.CLICONFIG.REDHAT_URL or "bugzilla.stage.redhat.com"


##################
# helper methods #
##################

def _split_int(s):
    return [int(i) for i in s.split(",")]


def _open_bz(**kwargs):
    return tests.utils.open_functional_bz(bugzilla.RHBugzilla, RHURL, kwargs)


if not _open_bz().logged_in:
    print("\nR/W tests require cached login credentials for url=%s\n" % RHURL)
    sys.exit(1)


def _check_have_admin(bz):
    funcname = inspect.stack()[1][3]

    # groupnames is empty for any user if our logged in user does not
    # have admin privs.
    # Check a known account that likely won't ever go away
    ret = bool(bz.getuser("anaconda-maint-list@redhat.com").groupnames)
    if not ret:
        print("\nNo admin privs, reduced testing of %s" % funcname)
    return ret


def _set_have_dev(bug, assigned_to):
    # This will only take effect if the logged in user has fedora dev perms
    have_dev = bug.assigned_to == assigned_to
    bug._testsuite_have_dev = have_dev  # pylint: disable=protected-access


def _bug_close(run_cli, bug):
    # Pre-close it
    bz = bug.bugzilla
    run_cli("bugzilla modify --close NOTABUG %s --minor-update" % bug.id, bz)
    bug.refresh()
    assert bug.status == "CLOSED"
    assert bug.resolution == "NOTABUG"


def _makebug(run_cli, bz):
    """
    Make a basic bug that the logged in user can maximally manipulate
    """
    product = "Fedora"
    component = "python-bugzilla"
    version = "rawhide"
    assigned_to = "triage@lists.fedoraproject.org"
    summary = ("python-bugzilla test basic bug %s" %
               datetime.datetime.today())
    newout = run_cli("bugzilla new "
        f"--product '{product}' "
        f"--component '{component}' "
        f"--version '{version}' "
        f"--assigned_to '{assigned_to}' "
        f"--summary \"{summary}\" "
        "--comment \"Test bug from the python-bugzilla test suite\" "
        "--outputformat \"%{bug_id}\"", bz)

    bugid = int(newout.splitlines()[-1])
    bug = bz.getbug(bugid)
    print("\nCreated bugid: %s" % bug.id)

    assert bug.component == component
    assert bug.version == version
    assert bug.summary == summary

    _set_have_dev(bug, assigned_to)
    _bug_close(run_cli, bug)

    return bug


def _check_have_dev(bug):
    funcname = inspect.stack()[1][3]
    have_dev = bug._testsuite_have_dev  # pylint: disable=protected-access

    if not have_dev:
        print("\nNo dev privs, reduced testing of %s" % funcname)
    return have_dev


class _BugCache:
    cache = {}

    @classmethod
    def get_bug(cls, run_cli, bz):
        key = bz.is_xmlrpc() and "xmlrpc" or "rest"
        if key not in cls.cache:
            cls.cache[key] = _makebug(run_cli, bz)
        return cls.cache[key]


def _make_subcomponent_bug(run_cli, bz):
    """
    Helper for creating a bug that can handle rhbz sub components
    """
    summary = ("python-bugzilla test manyfields bug %s" %
               datetime.datetime.today())
    assigned_to = "triage@lists.fedoraproject.org"
    url = "http://example.com"
    osval = "Windows"
    cc = "triage@lists.fedoraproject.org"
    assigned_to = "triage@lists.fedoraproject.org"
    blocked = "461686,461687"
    dependson = "427301"
    comment = "Test bug from python-bugzilla test suite"
    # We use this product+component to test sub_component
    product = "Bugzilla"
    component = "Extensions"
    version = "5.0"
    sub_component = "AgileTools"
    alias = "pybz-%s" % datetime.datetime.today().strftime("%s")
    newout = run_cli("bugzilla new "
        f"--product '{product}' "
        f"--version '{version}' "
        f"--component '{component}' "
        f"--sub-component '{sub_component}' "
        f"--summary \"{summary}\" "
        f"--comment \"{comment}\" "
        f"--url {url} "
        f"--os {osval} "
        f"--cc {cc} "
        f"--assigned_to {assigned_to} "
        f"--blocked {blocked} "
        f"--dependson {dependson} "
        f"--alias {alias} "
        "--arch ppc --severity Urgent --priority Low "
        "--outputformat \"%{bug_id}\"", bz)

    bugid = int(newout.splitlines()[-1])
    bug = bz.getbug(bugid, extra_fields=["sub_components"])
    print("\nCreated bugid: %s" % bugid)

    _set_have_dev(bug, assigned_to)
    have_dev = _check_have_dev(bug)

    assert bug.summary == summary
    assert bug.bug_file_loc == url
    assert bug.op_sys == osval
    assert all([e in bug.cc for e in cc.split(",")])
    assert bug.longdescs[0]["text"] == comment
    assert bug.sub_components == {component: [sub_component]}
    assert bug.alias == [alias]

    if have_dev:
        assert bug.blocks == _split_int(blocked)
        assert bug.depends_on == _split_int(dependson)
    else:
        # Using a non-dev account seems to fail to set these at bug create time
        assert bug.blocks == []
        assert bug.depends_on == []

    _bug_close(run_cli, bug)

    return bug


##############
# test cases #
##############

def test0LoggedInNoCreds(backends):
    bz = _open_bz(**backends, use_creds=False)
    assert not bz.logged_in


def test0ClassDetection():
    bz = bugzilla.Bugzilla(RHURL, use_creds=False)
    assert bz.__class__ is bugzilla.RHBugzilla


def test04NewBugAllFields(run_cli, backends):
    """
    Create a bug using all 'new' fields, check some values, close it
    """
    bz = _open_bz(**backends)
    bug = _make_subcomponent_bug(run_cli, bz)

    # Verify hasattr works
    assert hasattr(bug, "id")
    assert hasattr(bug, "bug_id")

    # Close the bug
    run_cli("bugzilla modify "
        "--close WONTFIX %s " %
        bug.id, bz)
    bug.refresh()
    assert bug.status == "CLOSED"
    assert bug.resolution == "WONTFIX"

    # Check bug's minimal history
    ret = bug.get_history_raw()
    assert len(ret["bugs"]) == 1
    assert len(ret["bugs"][0]["history"])


def test05ModifyStatus(run_cli, backends):
    """
    Modify status and comment fields for an existing bug
    """
    bz = _open_bz(**backends)
    bug = _BugCache.get_bug(run_cli, bz)
    have_dev = _check_have_dev(bug)
    cmd = "bugzilla modify %s " % bug.id

    origstatus = bug.status
    perm_error = "not allowed to (un)mark comments"

    # Set to ON_QA with a private comment
    try:
        status = "ON_QA"
        comment = ("changing status to %s at %s" %
                   (status, datetime.datetime.today()))
        run_cli(cmd +
            "--status %s --comment \"%s\" --private" % (status, comment), bz)

        bug.refresh()
        assert bug.status == status
        assert bug.longdescs[-1]["is_private"] == 1
        assert bug.longdescs[-1]["text"] == comment
    except RuntimeError as e:
        if have_dev:
            raise
        assert perm_error in str(e)

    # Close bug as DEFERRED with a private comment
    try:
        resolution = "DEFERRED"
        comment = ("changing status to CLOSED=%s at %s" %
                   (resolution, datetime.datetime.today()))
        run_cli(cmd +
            "--close %s --comment \"%s\" --private" %
            (resolution, comment), bz)

        bug.refresh()
        assert bug.status == "CLOSED"
        assert bug.resolution == resolution
        assert bug.comments[-1]["is_private"] == 1
        assert bug.comments[-1]["text"] == comment
    except RuntimeError as e:
        if have_dev:
            raise
        assert perm_error in str(e)

    # Set to assigned
    run_cli(cmd + "--status ASSIGNED", bz)
    bug.refresh()
    assert bug.status == "ASSIGNED"

    # Close bug as dup with no comment
    dupeid = "461686"
    desclen = len(bug.longdescs)
    run_cli(cmd +
        "--close DUPLICATE --dupeid %s" % dupeid, bz)

    bug.refresh()
    assert bug.dupe_of == int(dupeid)
    assert len(bug.longdescs) == (desclen + 1)
    assert "marked as a duplicate" in bug.longdescs[-1]["text"]

    # bz.setstatus test
    try:
        comment = ("adding lone comment at %s" % datetime.datetime.today())
        bug.setstatus("POST", comment=comment, private=True)
        bug.refresh()
        assert bug.longdescs[-1]["is_private"] == 1
        assert bug.longdescs[-1]["text"] == comment
        assert bug.status == "POST"
    except Exception as e:
        if have_dev:
            raise
        assert perm_error in str(e)

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

    # Confirm comments is same as get_comments
    assert bug.comments == bug.get_comments()
    # This method will be removed in a future version
    assert bug.comments == bug.getcomments()

    # Reset state
    run_cli(cmd + "--status %s" % origstatus, bz)
    bug.refresh()
    assert bug.status == origstatus


def test06ModifyEmails(run_cli, backends):
    """
    Modify cc, assignee, qa_contact for existing bug
    """
    bz = _open_bz(**backends)
    bug = _BugCache.get_bug(run_cli, bz)
    user = bug.creator
    have_dev = _check_have_dev(bug)

    cmd = "bugzilla modify %s " % bug.id

    # Test CC list and reset it
    email1 = "triage@lists.fedoraproject.org"
    run_cli(cmd + "--cc %s --cc %s" % (email1, user), bz)
    bug.refresh()
    assert email1 in bug.cc
    assert user in bug.cc

    # Remove CC via command line
    # Unprivileged user can only add/remove their own CC value
    run_cli(cmd + "--cc=-%s" % user, bz)
    bug.refresh()
    assert user not in bug.cc

    # Re-add CC via API
    bug.addcc(user)
    bug.refresh()
    assert user in bug.cc

    # Remove it again, via API
    bug.deletecc(user)
    bug.refresh()
    assert user not in bug.cc
    assert bug.cc

    perm_error = "required permissions may change that field"

    # Test assigned and QA target
    try:
        run_cli(cmd + "--assignee %s --qa_contact %s" % (email1, email1), bz)
        bug.refresh()
        assert bug.assigned_to == email1
        assert bug.qa_contact == email1
    except RuntimeError as e:
        if have_dev:
            raise
        assert perm_error in str(e)


    # Test --reset options
    try:
        run_cli(cmd + "--reset-qa-contact --reset-assignee", bz)
        bug.refresh()
        assert bug.assigned_to != email1
        assert bug.qa_contact != email1
    except RuntimeError as e:
        if have_dev:
            raise
        assert perm_error in str(e)


def test070ModifyMultiFlags(run_cli, backends):
    """
    Modify flags and fixed_in for 2 bugs
    """
    bz = _open_bz(**backends)
    bugid1 = _BugCache.get_bug(run_cli, bz).id
    bugid2 = _makebug(run_cli, bz).id
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
    setflags = "fedora_prioritized_bug? needinfo+"
    run_cli(cmd +
        " ".join([(" --flag " + f) for f in setflags.split()]), bz)

    bug1.refresh()
    bug2.refresh()

    assert flagstr(bug1) == setflags
    assert flagstr(bug2) == setflags
    assert bug1.get_flags("needinfo")[0]["status"] == "+"
    assert bug1.get_flag_status("fedora_prioritized_bug") == "?"

    # Clear flags
    if cleardict_new(bug1):
        bz.update_flags(bug1.id, cleardict_new(bug1))
    bug1.refresh()
    if cleardict_new(bug2):
        bz.update_flags(bug2.id, cleardict_new(bug2))
    bug2.refresh()

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert cleardict_old(bug1) == {}
    assert cleardict_old(bug2) == {}

    # Set "Fixed In" field
    origfix1 = bug1.fixed_in
    origfix2 = bug2.fixed_in

    newfix = origfix1 and (origfix1 + "-new1") or "blippy1"
    if newfix == origfix2:
        newfix = origfix2 + "-2"

    run_cli(cmd + "--fixed_in '%s'" % newfix, bz)

    bug1.refresh()
    bug2.refresh()
    assert bug1.fixed_in == newfix
    assert bug2.fixed_in == newfix

    # Reset fixed_in
    run_cli(cmd + "--fixed_in \"-\"", bz)

    bug1.refresh()
    bug2.refresh()
    assert bug1.fixed_in == "-"
    assert bug2.fixed_in == "-"


def test071ModifyMisc(run_cli, backends):
    bz = _open_bz(**backends)
    bug = _BugCache.get_bug(run_cli, bz)
    have_dev = _check_have_dev(bug)
    cmd = "bugzilla modify %s " % bug.id

    # modify --dependson
    run_cli(cmd + "--dependson 123456", bz)
    bug.refresh()
    assert 123456 in bug.depends_on
    run_cli(cmd + "--dependson =111222", bz)
    bug.refresh()
    assert [111222] == bug.depends_on
    run_cli(cmd + "--dependson=-111222", bz)
    bug.refresh()
    assert [] == bug.depends_on

    # modify --blocked
    run_cli(cmd + "--blocked 123,456", bz)
    bug.refresh()
    assert [123, 456] == bug.blocks
    run_cli(cmd + "--blocked =", bz)
    bug.refresh()
    assert [] == bug.blocks

    # modify --keywords
    origkw = bug.keywords
    run_cli(cmd + "--keywords +Documentation --keywords EasyFix", bz)
    bug.refresh()
    assert set(["Documentation", "EasyFix"] + origkw) == set(bug.keywords)
    run_cli(cmd + "--keywords=-EasyFix --keywords=-Documentation", bz)
    bug.refresh()
    assert origkw == bug.keywords

    perm_error = "user with the required permissions"

    try:
        # modify --target_release
        # modify --target_milestone
        targetbugid = 492463
        targetbug = bz.getbug(targetbugid)
        targetcmd = "bugzilla modify %s " % targetbugid
        run_cli(targetcmd +
                "--target_milestone beta --target_release 6.2", bz)
        targetbug.refresh()
        assert targetbug.target_milestone == "beta"
        assert targetbug.target_release == ["6.2"]
        run_cli(targetcmd +
                "--target_milestone rc --target_release 6.10", bz)
        targetbug.refresh()
        assert targetbug.target_milestone == "rc"
        assert targetbug.target_release == ["6.10"]
    except RuntimeError as e:
        if have_dev:
            raise
        assert perm_error in str(e)

    try:
        # modify --priority
        # modify --severity
        run_cli(cmd + "--priority low --severity high", bz)
        bug.refresh()
        assert bug.priority == "low"
        assert bug.severity == "high"
        run_cli(cmd + "--priority medium --severity medium", bz)
        bug.refresh()
        assert bug.priority == "medium"
        assert bug.severity == "medium"
    except RuntimeError as e:
        if have_dev:
            raise
        assert perm_error in str(e)

    # modify --os
    # modify --platform
    # modify --version
    run_cli(cmd + "--version rawhide --os Windows --arch ppc "
            "--url http://example.com", bz)
    bug.refresh()
    assert bug.version == "rawhide"
    assert bug.op_sys == "Windows"
    assert bug.platform == "ppc"
    assert bug.url == "http://example.com"
    run_cli(cmd + "--version rawhide --os Linux --arch s390 "
            "--url http://example.com/fribby", bz)
    bug.refresh()
    assert bug.version == "rawhide"
    assert bug.op_sys == "Linux"
    assert bug.platform == "s390"
    assert bug.url == "http://example.com/fribby"

    # modify --field
    run_cli(cmd + "--field cf_fixed_in=foo-bar-1.2.3 \
                  --field=cf_release_notes=baz", bz)

    bug.refresh()
    assert bug.fixed_in == "foo-bar-1.2.3"
    assert bug.cf_release_notes == "baz"


def test08Attachments(run_cli, backends):
    tmpdir = "__test_attach_output"
    if tmpdir in os.listdir("."):
        os.system("rm -r %s" % tmpdir)
    os.mkdir(tmpdir)
    os.chdir(tmpdir)

    try:
        _test8Attachments(run_cli, backends)
    finally:
        os.chdir("..")
        os.system("rm -r %s" % tmpdir)


def _test8Attachments(run_cli, backends):
    """
    Get and set attachments for a bug
    """
    bz = _open_bz(**backends)
    cmd = "bugzilla attach "
    testfile = "../tests/data/bz-attach-get1.txt"

    # Add attachment as CLI option
    setbug = _BugCache.get_bug(run_cli, bz)
    setbug = bz.getbug(setbug.id, extra_fields=["attachments"])
    orignumattach = len(setbug.attachments)

    # Add attachment from CLI with mime guessing
    desc1 = "python-bugzilla cli upload %s" % datetime.datetime.today()
    out1 = run_cli(cmd + "%s --description \"%s\" --file %s" %
                         (setbug.id, desc1, testfile), bz)
    out1 = out1.splitlines()[-1]

    desc2 = "python-bugzilla cli upload %s" % datetime.datetime.today()
    out2 = run_cli(cmd + "%s --file test --summary \"%s\"" %
                         (setbug.id, desc2), bz, stdin=open(testfile).read())

    # Expected output format:
    #   Created attachment <attachid> on bug <bugid>

    setbug.refresh()
    assert len(setbug.attachments) == (orignumattach + 2)

    att1 = setbug.attachments[-2]
    attachid = att1["id"]
    assert att1["summary"] == desc1
    assert att1["id"] == int(out1.splitlines()[0].split()[2])
    assert att1["content_type"] == "text/plain"

    att2 = setbug.attachments[-1]
    assert att2["summary"] == desc2
    assert att2["id"] == int(out2.splitlines()[0].split()[2])
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

    # Set attachment obsolete
    bz._backend.bug_attachment_update(  # pylint: disable=protected-access
        [setbug.attachments[-1]["id"]],
        {"is_obsolete": 1})
    setbug.refresh()
    assert setbug.attachments[-1]["is_obsolete"] == 1


    # Get attachment, verify content
    out = run_cli(cmd + "--get %s" % attachid, bz).splitlines()

    # Expect format:
    #   Wrote <filename>
    fname = out[0].split()[1].strip()

    assert len(out) == 1
    assert fname == "bz-attach-get1.txt"
    assert open(fname).read() == open(testfile).read()
    os.unlink(fname)

    # Get all attachments
    getbug = bz.getbug(setbug.id)
    getbug.autorefresh = True
    numattach = len(getbug.attachments)
    out = run_cli(cmd + "--getall %s" % getbug.id, bz).splitlines()

    assert len(out) == numattach
    fnames = [line.split(" ", 1)[1].strip() for line in out]
    assert len(fnames) == numattach
    for f in fnames:
        if not os.path.exists(f):
            raise AssertionError("filename '%s' not found" % f)
        os.unlink(f)

    # Get all attachments, but ignore obsolete
    ignorecmd = cmd + "--getall %s --ignore-obsolete" % getbug.id
    out = run_cli(ignorecmd, bz).splitlines()

    assert len(out) == (numattach - 1)
    fnames = [line.split(" ", 1)[1].strip() for line in out]
    assert len(fnames) == (numattach - 1)
    for f in fnames:
        if not os.path.exists(f):
            raise AssertionError("filename '%s' not found" % f)
        os.unlink(f)


def test09Whiteboards(run_cli, backends):
    bz = _open_bz(**backends)
    bug = _BugCache.get_bug(run_cli, bz)
    have_dev = _check_have_dev(bug)
    cmd = "bugzilla modify %s " % bug.id

    # Set all whiteboards
    initval = str(random.randint(1, 1024))
    statusstr = initval + "foo, bar, baz bar1"
    devstr = initval + "devel"
    internalstr = initval + "internal"
    qastr = initval + "qa"
    run_cmd = (cmd + f"--whiteboard '{statusstr}' ")
    if have_dev:
        run_cmd += (
            f"--devel_whiteboard '{devstr}' "
            f"--internal_whiteboard '{internalstr}' "
            f"--qa_whiteboard '{qastr}' ")
    run_cli(run_cmd, bz)

    bug.refresh()
    assert bug.whiteboard == statusstr

    if have_dev:
        assert bug.qa_whiteboard == qastr
        assert bug.devel_whiteboard == devstr
        assert bug.internal_whiteboard == internalstr

    # Remove a tag
    run_cli(cmd + "--whiteboard=-bar, ", bz)
    bug.refresh()
    statusstr = statusstr.replace("bar, ", "")
    assert bug.status_whiteboard == statusstr

    run_cli(cmd + "--whiteboard NEWBIT", bz)
    bug.refresh()
    statusstr += " NEWBIT"
    assert bug.whiteboard == statusstr

    # Clear whiteboards
    update = bz.build_update(
        whiteboard="", devel_whiteboard="",
        internal_whiteboard="", qa_whiteboard="")
    bz.update_bugs(bug.id, update)

    bug.refresh()
    assert bug.whiteboard == ""
    if have_dev:
        assert bug.qa_whiteboard == ""
        assert bug.devel_whiteboard == ""
        assert bug.internal_whiteboard == ""


def test10Login(run_cli, monkeypatch):
    """
    Failed login test, gives us a bit more coverage
    """
    tests.utils.monkeypatch_getpass(monkeypatch)

    cmd = "bugzilla --no-cache-credentials --bugzilla %s" % RHURL
    # Implied login with --username and --password
    ret = run_cli("%s --user foobar@example.com "
            "--password foobar query -b 123456" % cmd,
            None, expectfail=True)
    assert "Login failed: " in ret

    # 'login' with explicit options
    ret = run_cli("%s --user foobar@example.com "
            "--password foobar login" % cmd,
            None, expectfail=True)
    assert "Login failed: " in ret

    # 'login' with positional options
    ret = run_cli("%s login foobar@example.com foobar" % cmd,
            None, expectfail=True)
    assert "Login failed: " in ret

    # bare 'login'
    stdinstr = "foobar@example.com\n\rfoobar\n\r"
    ret = run_cli("%s login" % cmd,
            None, expectfail=True, stdin=stdinstr)
    assert "Bugzilla Username:" in ret
    assert "Bugzilla Password:" in ret
    assert "Login failed: " in ret


def test11UserUpdate(backends):
    # This won't work if run by the same user we are using
    bz = _open_bz(**backends)
    email = "anaconda-maint-list@redhat.com"
    group = "fedora_contrib"

    have_admin = _check_have_admin(bz)

    user = bz.getuser(email)
    if have_admin:
        assert group in user.groupnames
    origgroups = user.groupnames

    # Test group_get
    try:
        groupobj = bz.getgroup(group)
        groupobj.refresh()
    except Exception as e:
        if have_admin:
            raise
        assert bugzilla.BugzillaError.get_bugzilla_error_code(e) == 805

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

    # Try user create
    try:
        name = "pythonbugzilla-%s" % datetime.datetime.today()
        bz.createuser(name + "@example.com", name, name)
    except Exception as e:
        if have_admin:
            raise
        assert "Sorry, you aren't a member" in str(e)


def test11ComponentEditing(backends):
    bz = _open_bz(**backends)
    component = ("python-bugzilla-testcomponent-%s" %
                 str(random.randint(1, 1024 * 1024 * 1024)))
    basedata = {
        "product": "Fedora Documentation",
        "component": component,
    }

    have_admin = _check_have_admin(bz)

    def compare(data, newid):
        # pylint: disable=protected-access
        products = bz._proxy.Product.get({"names": [basedata["product"]]})
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
        if bz.is_rest():
            # redhat REST does not support component editing
            assert "A REST API resource was not found" in str(e)
        elif have_admin:
            raise
        else:
            assert (("Sorry, you aren't a member" in str(e)) or
                # bugzilla 5 error string
                ("You are not allowed" in str(e)))


def test13SubComponents(run_cli, backends):
    bz = _open_bz(**backends)
    bug = _make_subcomponent_bug(run_cli, bz)

    bug.autorefresh = True
    assert bug.component == "Extensions"

    bz.update_bugs(bug.id, bz.build_update(
        component="Extensions", sub_component="RedHat"))
    bug.refresh()
    assert bug.sub_components == {"Extensions": ["RedHat"]}

    bz.update_bugs(bug.id, bz.build_update(
        component="Extensions", sub_component="AgileTools"))
    bug.refresh()
    assert bug.sub_components == {"Extensions": ["AgileTools"]}


def _testExternalTrackers(run_cli, bz):
    bugid = _BugCache.get_bug(run_cli, bz).id
    ext_bug_id = 380489

    # Delete any existing external trackers to get to a known state
    ids = [bug['id'] for bug in bz.getbug(bugid).external_bugs]
    if ids != []:
        bz.remove_external_tracker(ids=ids)

    url = "https://bugzilla.mozilla.org"
    if bz.bz_ver_major < 5:
        url = "http://bugzilla.mozilla.org"

    # test adding tracker
    kwargs = {
        'ext_type_id': 6,
        'ext_type_url': url,
        'ext_type_description': 'Mozilla Foundation',
    }
    bz.add_external_tracker(bugid, ext_bug_id, **kwargs)
    added_bug = bz.getbug(bugid).external_bugs[0]
    assert added_bug['type']['id'] == kwargs['ext_type_id']
    assert added_bug['type']['url'] == kwargs['ext_type_url']
    assert (added_bug['type']['description'] ==
        kwargs['ext_type_description'])

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


def test14ExternalTrackersAddUpdateRemoveQuery(run_cli, backends):
    bz = _open_bz(**backends)
    try:
        _testExternalTrackers(run_cli, bz)
    except Exception as e:
        if not bz.is_rest():
            raise
        assert "No REST API available" in str(e)


def test15EnsureLoggedIn(run_cli, backends):
    bz = _open_bz(**backends)
    comm = "bugzilla --ensure-logged-in query --bug_id 979546"
    run_cli(comm, bz)

    # Test that we don't pollute the query dict with auth info
    query = {"id": [1234567]}
    origquery = query.copy()
    bz.query(query)
    assert query == origquery


def test16ModifyTags(run_cli, backends):
    bz = _open_bz(**backends)
    bug = _BugCache.get_bug(run_cli, bz)
    cmd = "bugzilla modify %s " % bug.id

    try:
        if bug.tags:
            bz.update_tags(bug.id, tags_remove=bug.tags)
            bug.refresh()
            assert bug.tags == []

        run_cli(cmd + "--tags foo --tags +bar --tags baz", bz)
        bug.refresh()
        assert bug.tags == ["foo", "bar", "baz"]

        run_cli(cmd + "--tags=-bar", bz)
        bug.refresh()
        assert bug.tags == ["foo", "baz"]

        bz.update_tags(bug.id, tags_remove=bug.tags)
        bug.refresh()
        assert bug.tags == []
    except Exception as e:
        if not bz.is_rest():
            raise
        assert "No REST API available" in str(e)


def test17LoginAPIKey(backends):
    api_key = "somefakeapikey1234"
    bz = _open_bz(use_creds=False, api_key=api_key, **backends)
    try:
        assert bz.logged_in is False

        # Use this to trigger a warning about api_key
        bz.createbug(bz.build_createbug())
    except Exception as e:
        assert "The API key you specified is invalid" in str(e)
