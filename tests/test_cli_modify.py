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

    # Modify with a slew of misc opt coverage
    cmd = "bugzilla modify 1165434 "
    cmd += "--assigned_to foo@example.com --qa_contact qa@example.com "
    cmd += "--product newproduct "
    cmd += "--blocked +1234 --blocked -1235 --blocked = "
    cmd += "--url https://example.com "
    cmd += "--cc=+bar@example.com --cc=-steve@example.com "
    cmd += "--dependson=+2234 --dependson=-2235 --dependson = "
    cmd += "--groups +foogroup "
    cmd += "--keywords +newkeyword --keywords=-byekeyword --keywords = "
    cmd += "--os windows --arch mips "
    cmd += "--priority high --severity low "
    cmd += "--summary newsummary --version 1.2.3 "
    cmd += "--reset-assignee --reset-qa-contact "
    cmd += "--alias fooalias "
    cmd += "--target_release 1.2.4 --target_milestone beta "
    cmd += "--devel_whiteboard =DEVBOARD --internal_whiteboard =INTBOARD "
    cmd += "--qa_whiteboard =QABOARD "
    cmd += "--comment-tag FOOTAG --field bar=foo "
    cmd += "--minor-update "
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_update_args="data/mockargs/test_modify5.txt",
        bug_update_return={})
    out = run_cli(cmd, fakebz)
    assert not out
