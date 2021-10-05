# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import tempfile

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
    cmd += "login FOO BAR"
    tmp = tempfile.NamedTemporaryFile()
    fakebz = tests.mockbackend.make_bz(
        bz_kwargs={"use_creds": True, "tokenfile": tmp.name},
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={'id': 1234, 'token': 'my-fake-token'},
        user_get_args=None,
        user_get_return={})
    fakebz.connect("https://example.com")
    out = run_cli(cmd, fakebz)
    assert "Token cache saved" in out
    assert fakebz.tokenfile in out
    assert "Consider using bugzilla API" in out
    tests.utils.diff_compare(open(tmp.name).read(),
            "data/clioutput/tokenfile.txt")

    # Returns success for logged_in check and hits another tokenfile line
    cmd = "bugzilla --ensure-logged-in "
    cmd += "login FOO BAR"
    fakebz = tests.mockbackend.make_bz(
        bz_kwargs={"use_creds": True, "tokenfile": None},
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={'id': 1234, 'token': 'my-fake-token'},
        user_get_args=None,
        user_get_return={})
    out = run_cli(cmd, fakebz)
    assert "Token not saved" in out


def test_interactive_login(monkeypatch, run_cli):
    bz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_interactive_login.txt",
        user_login_return={},
        user_logout_args=None,
        user_logout_return={},
        user_get_args=None,
        user_get_return={})

    tests.utils.monkeypatch_getpass(monkeypatch)
    cmd = "bugzilla login"
    fakestdin = "fakeuser\nfakepass\n"
    out = run_cli(cmd, bz, stdin=fakestdin)
    assert "Bugzilla Username:" in out
    assert "Bugzilla Password:" in out

    # API key prompting and saving
    tmp = tempfile.NamedTemporaryFile()
    bz.configpath = [tmp.name]
    bz.url = "https://example.com"

    cmd = "bugzilla login --api-key"
    fakestdin = "MY-FAKE-KEY\n"
    out = run_cli(cmd, bz, stdin=fakestdin)
    assert "API Key:" in out
    assert tmp.name in out
    tests.utils.diff_compare(open(tmp.name).read(),
            "data/clioutput/test_interactive_login_apikey_rcfile.txt")

    # Check that we don't attempt to log in if API key is configured
    assert bz.api_key
    cmd = "bugzilla login"
    out = run_cli(cmd, bz)
    assert "already have an API" in out
