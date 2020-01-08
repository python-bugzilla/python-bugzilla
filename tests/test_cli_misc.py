#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Test miscellaneous CLI bits to get build out our code coverage
"""

from __future__ import print_function

import requests

import bugzilla
import tests
import tests.mockbackend


def testHelp(run_cli):
    out = run_cli("bugzilla --help", None)
    assert len(out.splitlines()) > 18


def testCmdHelp(run_cli):
    out = run_cli("bugzilla query --help", None)
    assert len(out.splitlines()) > 40


def testVersion(run_cli):
    out = run_cli("bugzilla --version", None)
    assert out.strip() == bugzilla.__version__


def testPositionalArgs(run_cli):
    # Make sure cli correctly rejects ambiguous positional args
    out = run_cli("bugzilla login --xbadarg foo",
            None, expectfail=True)
    assert "unrecognized arguments: --xbadarg" in out

    out = run_cli("bugzilla modify 123456 --foobar --status NEW",
            None, expectfail=True)
    assert "unrecognized arguments: --foobar" in out


def testDebug(run_cli):
    # Coverage testing for debug options
    run_cli("bugzilla --bugzilla https:///BADURI --verbose login",
            None, expectfail=True)
    run_cli("bugzilla --bugzilla https:///BADURI --debug login",
            None, expectfail=True)


def testExceptions(run_cli):
    """
    Test exception handling around main()
    """
    fakebz = tests.mockbackend.make_bz(
        bug_search_args=None,
        bug_search_return=KeyboardInterrupt())
    out = run_cli("bugzilla query --bug_id 1", fakebz, expectfail=True)
    assert "user request" in out

    fakebz = tests.mockbackend.make_bz(
        bug_search_args=None,
        bug_search_return=bugzilla.BugzillaError("foo"))
    out = run_cli("bugzilla query --bug_id 1", fakebz, expectfail=True)
    assert "Server error:" in out

    fakebz = tests.mockbackend.make_bz(
        bug_search_args=None,
        bug_search_return=requests.exceptions.SSLError())
    out = run_cli("bugzilla query --bug_id 1", fakebz, expectfail=True)
    assert "trust the remote server" in out

    fakebz = tests.mockbackend.make_bz(
        bug_search_args=None,
        bug_search_return=requests.exceptions.ConnectionError())
    out = run_cli("bugzilla query --bug_id 1", fakebz, expectfail=True)
    assert "Connection lost" in out


def testManualURL(run_cli):
    """
    Test passing a manual URL, to hit those non-testsuite code paths
    """
    try:
        cmd = "bugzilla --bztype foobar "
        cmd += "--bugzilla https:///FAKEURL query --bug_id 1"
        run_cli(cmd, None)
    except Exception as e:
        assert "No host supplied" in str(e)
