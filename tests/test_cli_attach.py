# -*- coding: utf-8 -*-

# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import os

import tests
import tests.mockbackend
import tests.utils


##################################
# 'bugzilla attach' mock testing #
##################################

def test_attach(run_cli):
    attachfile = os.path.dirname(__file__) + "/data/bz-attach-get1.txt"
    attachcontent = open(attachfile).read()

    # Hit error when no ID specified
    fakebz = tests.mockbackend.make_bz()
    out = run_cli("bugzilla attach", fakebz, expectfail=True)
    assert "ID must be specified" in out

    # Hit error when using tty and no --file specified
    out = run_cli("bugzilla attach 123456", fakebz, expectfail=True)
    assert "--file must be specified" in out

    # Hit error when using stdin, but no --desc
    out = run_cli("bugzilla attach 123456", fakebz, expectfail=True,
            stdin=attachcontent)
    assert "--description must be specified" in out

    # Basic CLI attach
    cmd = "bugzilla attach 123456 --file=%s " % attachfile
    cmd += "--type text/x-patch --private "
    cmd += "--comment 'some comment to go with it'"
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_create_args="data/mockargs/test_attach1.txt",
        bug_attachment_create_return={'ids': [1557949]})
    out = run_cli(cmd, fakebz)
    assert "Created attachment 1557949 on bug 123456" in out

    # Attach from stdin
    cmd = "bugzilla attach 123456 --file=fake-file-name.txt "
    cmd += "--description 'Some attachment description' "
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_create_args="data/mockargs/test_attach2.txt",
        bug_attachment_create_return={'ids': [1557949]})
    out = run_cli(cmd, fakebz, stdin=attachcontent)
    assert "Created attachment 1557949 on bug 123456" in out


def _test_attach_get(run_cli):
    # Hit error when using ids with --get*
    fakebz = tests.mockbackend.make_bz()
    out = run_cli("bugzilla attach 123456 --getall 123456",
            fakebz, expectfail=True)
    assert "not used for" in out

    # Basic --get ATTID usage
    filename = u"Klíč memorial test file.txt"
    cmd = "bugzilla attach --get 112233"
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_get_args="data/mockargs/test_attach_get1.txt",
        bug_attachment_get_return="data/mockreturn/test_attach_get1.txt")
    out = run_cli(cmd, fakebz)
    assert filename in out

    # Basic --getall with --ignore-obsolete
    cmd = "bugzilla attach --getall 663674 --ignore-obsolete"
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_get_all_args="data/mockargs/test_attach_get2.txt",
        bug_attachment_get_all_return="data/mockreturn/test_attach_get2.txt")
    out = run_cli(cmd, fakebz)

    os.system("ls %s" % os.getcwd())
    filename += ".1"
    assert filename in out
    assert "bugzilla-filename" in out


def test_attach_get(run_cli):
    import tempfile
    import shutil
    tmpdir = tempfile.mkdtemp(dir=os.getcwd())
    origcwd = os.getcwd()
    os.chdir(tmpdir)
    try:
        _test_attach_get(run_cli)
    finally:
        os.chdir(origcwd)
        shutil.rmtree(tmpdir)
