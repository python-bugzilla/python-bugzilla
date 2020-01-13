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

import base64
import datetime
import json

import pytest
import requests

import bugzilla
from bugzilla._compatimports import Binary, DateTime

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


def test_json_xmlrpc(run_cli):
    # Test --json output with XMLRPC type conversion
    cmd = "bugzilla query --json --id 1165434"

    timestr = '20181209T19:12:12'
    dateobj = datetime.datetime.strptime(timestr, '%Y%m%dT%H:%M:%S')

    attachfile = tests.utils.tests_path("data/bz-attach-get1.txt")
    attachdata = open(attachfile, "rb").read()

    bugid = 1165434
    data = {"bugs": [{
        'id': bugid,
        'timetest': DateTime(dateobj),
        'binarytest': Binary(attachdata),
    }]}

    fakebz = tests.mockbackend.make_bz(
        bug_search_args=None,
        bug_search_return={"bugs": [{"id": bugid}]},
        bug_get_args=None,
        bug_get_return=data)
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(tests.utils.sanitize_json(out),
        "data/clioutput/test_json_xmlrpc.txt")

    retdata = json.loads(out)["bugs"][0]
    assert (base64.b64decode(retdata["binarytest"]) ==
            attachdata)
    assert retdata["timetest"] == dateobj.isoformat() + "Z"


    # Test an error case, json converter can't handle Exception class
    data["bugs"][0]["foo"] = Exception("foo")
    fakebz = tests.mockbackend.make_bz(
        bug_search_args=None,
        bug_search_return={"bugs": [{"id": bugid}]},
        bug_get_args=None,
        bug_get_return=data)
    with pytest.raises(RuntimeError):
        run_cli(cmd, fakebz, expectfail=True)
