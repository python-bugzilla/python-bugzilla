#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Test miscellaneous API bits
"""

import os
import tempfile

import pytest

import bugzilla

import tests
import tests.mockbackend


def testCookies():
    dirname = os.path.dirname(__file__)
    cookiesbad = dirname + "/data/cookies-bad.txt"
    cookieslwp = dirname + "/data/cookies-lwp.txt"
    cookiesmoz = dirname + "/data/cookies-moz.txt"

    # We used to convert LWP cookies, but it shouldn't matter anymore,
    # so verify they fail at least
    with pytest.raises(bugzilla.BugzillaError):
        tests.mockbackend.make_bz(version="3.0.0",
                bz_kwargs={"cookiefile": cookieslwp, "use_creds": True})

    with pytest.raises(bugzilla.BugzillaError):
        tests.mockbackend.make_bz(version="3.0.0",
                bz_kwargs={"cookiefile": cookiesbad, "use_creds": True})

    # Mozilla should 'just work'
    tests.mockbackend.make_bz(version="3.0.0",
            bz_kwargs={"cookiefile": cookiesmoz, "use_creds": True})


def test_readconfig():
    # Testing for bugzillarc handling
    bzapi = tests.mockbackend.make_bz(version="4.4.0", rhbz=True)
    bzapi.url = "example.com"
    temp = tempfile.NamedTemporaryFile(mode="w")

    content = """
[example.com]
foo=1
user=test1
password=test2"""
    temp.write(content)
    temp.flush()
    bzapi.readconfig(temp.name)
    assert bzapi.user == "test1"
    assert bzapi.password == "test2"
    assert bzapi.api_key is None

    bzapi.url = "foo.example.com"
    bzapi.user = None
    bzapi.readconfig(temp.name)
    assert bzapi.user is None

    content = """
[foo.example.com]
user=test3
password=test4
api_key=123abc
"""
    temp.write(content)
    temp.flush()
    bzapi.readconfig(temp.name)
    assert bzapi.user == "test3"
    assert bzapi.password == "test4"
    assert bzapi.api_key == "123abc"

    bzapi.url = "bugzilla.redhat.com"
    bzapi.user = None
    bzapi.password = None
    bzapi.api_key = None
    bzapi.readconfig(temp.name)
    assert bzapi.user is None
    assert bzapi.password is None
    assert bzapi.api_key is None
