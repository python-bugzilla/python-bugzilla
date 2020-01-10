# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import tests
import tests.mockbackend
import tests.utils


##################################
# 'bugzilla modify' mock testing #
##################################

def test_modify(run_cli):
    # errors on missing args
    cmd = "bugzilla modify 123456"
    fakebz = tests.mockbackend.make_bz()
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "additional arguments" in out

    # Modify basic
    cmd = "bugzilla modify 123456 1234567 "
    cmd += "--status ASSIGNED --component NEWCOMP "
    fakebz = tests.mockbackend.make_bz(
        bug_update_args="data/mockargs/test_modify1.txt",
        bug_update_return={})
    out = run_cli(cmd, fakebz)
    assert not out

    # Modify with lots of opts
    cmd = "bugzilla modify 123456 --component NEWCOMP "
    cmd += "--keyword +FOO --groups=-BAR --blocked =123456,445566 "
    cmd += "--flag=-needinfo,+somethingelse "
    cmd += "--whiteboard =foo --whiteboard =thisone "
    cmd += "--dupeid 555666 "
    cmd += "--comment 'some example comment' --private "
    fakebz = tests.mockbackend.make_bz(
        bug_update_args="data/mockargs/test_modify2.txt",
        bug_update_return={})
    out = run_cli(cmd, fakebz)
    assert not out

    # Modify with tricky opts hitting other API calls
    cmd = "bugzilla modify 1165434 "
    cmd += "--tags +addtag --tags=-rmtag "
    cmd += "--qa_whiteboard +yo-qa --qa_whiteboard=-foo "
    cmd += "--internal_whiteboard +internal-hey --internal_whiteboard +bar "
    cmd += "--devel_whiteboard +devel-duh --devel_whiteboard=-yay "
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_update_tags_args="data/mockargs/test_modify3-tags.txt",
        bug_update_tags_return={},
        bug_update_args="data/mockargs/test_modify3.txt",
        bug_update_return={},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    assert not out

    # Modify hitting some rhbz paths
    cmd = "bugzilla modify 1165434 "
    cmd += "--fixed_in foofixedin "
    cmd += "--component lvm2 "
    cmd += "--sub-component some-sub-component"
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_update_args="data/mockargs/test_modify4.txt",
        bug_update_return={})
    out = run_cli(cmd, fakebz)
    assert not out
