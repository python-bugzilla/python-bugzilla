#
# Copyright Red Hat, Inc. 2014
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests for testing some bug.py magic
"""

import io
import pickle

import pytest

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
    fd = io.BytesIO()
    pickle.dump(bug, fd)
    fd.seek(0)
    bug = pickle.load(fd)
    assert getattr(bug, "bugzilla") is None
    assert str(bug)
    assert repr(bug)
    bug.bugzilla = rhbz
    _assert_bug()


def testBugNoID():
    try:
        Bug(bugzilla=rhbz, dict={"component": "foo"})
        raise AssertionError("Expected lack of ID failure.")
    except TypeError:
        pass


def test_api_getbugs():
    fakebz = tests.mockbackend.make_bz(
        bug_get_args="data/mockargs/test_api_getbugs1.txt",
        bug_get_return="data/mockreturn/test_query_cve_getbug.txt")

    fakebz.bug_autorefresh = True
    bug = fakebz.getbug("CVE-1234-5678", exclude_fields="foo")
    assert bug.alias == ["CVE-1234-5678"]
    assert bug.autorefresh is True

    fakebz = tests.mockbackend.make_bz(
        bug_get_args="data/mockargs/test_api_getbugs2.txt",
        bug_get_return={"bugs": [{}, {}]})
    assert fakebz.getbugs(["123456", "CVE-1234-FAKE"]) == []


def test_bug_getattr():
    fakebz = tests.mockbackend.make_bz(
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug_rhel.txt")
    bug = fakebz.getbug(1165434)

    with pytest.raises(AttributeError):
        # Hits a specific codepath in Bug.__getattr__
        dummy = bug.__baditem__

    bug.autorefresh = True
    summary = bug.summary
    del(bug.__dict__["summary"])
    # Trigger autorefresh
    assert bug.summary == summary


def test_bug_apis():
    def _get_fake_bug(apiname):
        update_args = "data/mockargs/test_bug_apis_%s_update.txt" % apiname
        fakebz = tests.mockbackend.make_bz(rhbz=True,
            bug_get_args=None,
            bug_get_return="data/mockreturn/test_getbug_rhel.txt",
            bug_update_args=update_args,
            bug_update_return={})
        return fakebz.getbug(1165434)

    # bug.setstatus, wrapper for update_bugs
    bug = _get_fake_bug("setstatus")
    bug.setstatus("POST", "foocomment", private=True)

    # bug.close, wrapper for update_bugs
    bug = _get_fake_bug("close")
    bug.close("UPSTREAM", dupeid=123456, comment="foocomment2",
            isprivate=False, fixedin="1.2.3.4.5")

    # bug.setassignee, wrapper for update_bugs
    bug = _get_fake_bug("setassignee")
    bug.setassignee(
        assigned_to="foo@example.com", qa_contact="bar@example.com",
        comment="foocomment")
    with pytest.raises(ValueError):
        # Hits a validation path
        bug.setassignee()

    # bug.addcc test
    bug = _get_fake_bug("addcc")
    bug.addcc("foo2@example.com", comment="foocomment")

    # bug.deletecc test
    bug = _get_fake_bug("deletecc")
    bug.deletecc("foo2@example.com", comment="foocomment")

    # bug.addcomment test
    bug = _get_fake_bug("addcomment")
    bug.addcomment("test comment", private=True)

    # bug.updateflags test
    bug = _get_fake_bug("updateflags")
    bug.updateflags({"someflag": "someval"})

    # Some minor flag API tests
    assert "creation_date" in bug.get_flag_type("needinfo")
    assert bug.get_flag_type("NOPE") is None
    assert bug.get_flags("NOPE") is None
    assert bug.get_flag_status("NOPE") is None

    # Minor get_history_raw wrapper
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_history_args="data/mockargs/test_bug_api_history.txt",
        bug_history_return={},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug_rhel.txt",
        bug_comments_args="data/mockargs/test_bug_api_comments.txt",
        bug_comments_return={"bugs": {"1165434": {"comments": []}}},
        bug_attachment_get_all_args=(
            "data/mockargs/test_bug_api_get_attachments.txt"),
        bug_attachment_get_all_return="data/mockreturn/test_attach_get2.txt",
    )

    # Stub API testing
    bug = fakebz.getbug(1165434)
    bug.get_history_raw()
    bug.getcomments()

    # Some hackery to hit a few attachment code paths
    bug.id = 663674
    attachments = bug.get_attachments()
    bug.attachments = attachments
    assert [469147, 470041, 502352] == bug.get_attachment_ids()
