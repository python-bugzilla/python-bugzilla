# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import pytest

import bugzilla

import tests
import tests.mockbackend
import tests.utils


#################################
# 'bugzilla login' mock testing #
#################################

def test_login(run_cli):
    cmd = "bugzilla login FOO BAR"

    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login.txt",
        user_login_return=RuntimeError("TEST ERROR"))
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "Login failed: TEST ERROR" in out

    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={})
    out = run_cli(cmd, fakebz)
    assert "Login successful" in out

    cmd = "bugzilla --restrict-login --user FOO --password BAR login"
    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login-restrict.txt",
        user_login_return={})
    out = run_cli(cmd, fakebz)
    assert "Login successful" in out

    cmd = "bugzilla --ensure-logged-in --user FOO --password BAR login"
    # Raises raw error trying to see if we aren't logged in
    with pytest.raises(NotImplementedError):
        fakebz = tests.mockbackend.make_bz(
            user_login_args="data/mockargs/test_login.txt",
            user_login_return={},
            user_get_args=None,
            user_get_return=NotImplementedError())
        out = run_cli(cmd, fakebz)

    # Errors with expected code
    cmd = "bugzilla --ensure-logged-in --user FOO --password BAR login"
    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={},
        user_get_args=None,
        user_get_return=bugzilla.BugzillaError("TESTMESSAGE", code=505))
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "--ensure-logged-in passed but you" in out

    # Returns success for logged_in check and hits a tokenfile line
    cmd = "bugzilla --ensure-logged-in "
    cmd += "--user FOO --password BAR login"
    fakebz = tests.mockbackend.make_bz(
        bz_kwargs={"use_creds": True},
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={},
        user_get_args=None,
        user_get_return={})
    out = run_cli(cmd, fakebz)
    assert "token cache updated" in out
