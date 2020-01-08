#
# Copyright Red Hat, Inc. 2014
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests for testing some bug.py magic
"""

import pickle
import sys

import tests
import tests.mockbackend
import tests.utils

from bugzilla.bug import Bug


rhbz = tests.mockbackend.make_bz(version="4.4.0", rhbz=True)


def testBasic():
    data = {
        "bug_id": 123456,
        "status": "NEW",
        "assigned_to": "foo@bar.com",
        "component": "foo",
        "product": "bar",
        "short_desc": "some short desc",
        "cf_fixed_in": "nope",
        "fixed_in": "1.2.3.4",
        "devel_whiteboard": "some status value",
    }

    bug = Bug(bugzilla=rhbz, dict=data)

    def _assert_bug():
        assert hasattr(bug, "component") is True
        assert getattr(bug, "components") == ["foo"]
        assert getattr(bug, "product") == "bar"
        assert hasattr(bug, "short_desc") is True
        assert getattr(bug, "summary") == "some short desc"
        assert bool(getattr(bug, "cf_fixed_in")) is True
        assert getattr(bug, "fixed_in") == "1.2.3.4"
        assert bool(getattr(bug, "cf_devel_whiteboard")) is True
        assert getattr(bug, "devel_whiteboard") == "some status value"

    _assert_bug()

    assert str(bug) == "#123456 NEW        - foo@bar.com - some short desc"
    assert repr(bug).startswith("<Bug #123456")

    # This triggers some code in __getattr__
    dir(bug)

    # Test special pickle support
    if sys.version_info[0] >= 3:
        import io
        fd = io.BytesIO()
    else:
        import StringIO  # pylint: disable=import-error
        fd = StringIO.StringIO()

    pickle.dump(bug, fd)
    fd.seek(0)
    bug = pickle.load(fd)
    assert getattr(bug, "bugzilla") is None
    bug.bugzilla = rhbz
    _assert_bug()


def testBugNoID():
    try:
        Bug(bugzilla=rhbz, dict={"component": "foo"})
        raise AssertionError("Expected lack of ID failure.")
    except TypeError:
        pass
