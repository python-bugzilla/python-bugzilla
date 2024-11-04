# pylint: disable=unused-argument
from uuid import uuid4
from xmlrpc.client import Fault

from pytest import raises
from pytest import mark

from bugzilla import Bugzilla, BugzillaError
from bugzilla.bug import Bug

from ..utils import open_bz
from . import TEST_URL

# NOTE: The tests in this file assume that an API key is defined in the bugzillarc!


DEFAULT_PARAMS = {"product": "TestProduct",
                  "component": "TestComponent",
                  "version": "unspecified",
                  "summary": "A new bug",
                  "description": "Details on how to reproduce",
                  "cc": "nemo@example.com",
                  "op_sys": "Linux",
                  "platform": "PC"}


def _create_bug(bz: Bugzilla, **kwargs) -> Bug:
    """
    Create a new bug with overwrite-able defaults
    """
    params = DEFAULT_PARAMS.copy()
    params.update(kwargs)

    return bz.createbug(**bz.build_createbug(**params))


def test_create_bug(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    bug = _create_bug(bz)

    assert isinstance(bug, Bug)
    assert bug.id

    bug = bz.getbug(bug.id)
    for field in ("product", "component", "version", "summary"):
        assert getattr(bug, field) == DEFAULT_PARAMS[field]


def test_create_bug_anonymous(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, configpaths="/dev/null", **backends)
    with raises((Fault, BugzillaError)):
        _create_bug(bz)


def test_create_bug_alias(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    alias = uuid4().hex
    bug = _create_bug(bz, alias=alias)

    bug = bz.getbug(bug.id)
    assert alias in bug.alias

    with raises((Fault, BugzillaError)):
        _create_bug(bz, alias=alias)


def test_update_bug(mocked_responses, backends):
    email = "nemo@example.com"
    bz = open_bz(url=TEST_URL, **backends)
    bug = _create_bug(bz)
    params = bz.build_update(resolution="WONTFIX", status="RESOLVED", cc_remove=email)
    bz.update_bugs(bug.id, params)
    bug.refresh()

    assert bug.resolution == "WONTFIX"
    assert bug.status == "RESOLVED"
    assert bug.cc == []

    params = bz.build_update(cc_add=email)
    bz.update_bugs(bug.id, params)
    bug.refresh()

    assert bug.cc == [email]


# Bugzilla instance has no CLOSED status
@mark.xfail
def test_close_bug(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    bug = _create_bug(bz)
    bug.close(resolution="WORKSFORME", comment="Bla bla", isprivate=True)
    bug.refresh()

    assert bug.resolution == "WORKSFORME"
    assert bug.status == "CLOSED"


def test_add_comment(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    bug = bz.getbug(1)

    comment_count = len(bug.get_comments())
    bug.addcomment("Bla Bla bla", private=True)
    bug.refresh()

    assert len(bug.get_comments()) == comment_count + 1


def test_update_flags(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    bug = _create_bug(bz)
    flag = {"requestee": "nemo@example.com", "name": "needinfo", "status": "?"}
    params = bz.build_update(flags=[flag])
    bz.update_bugs([bug.id], params)
    bug.refresh()

    assert len(bug.flags) == 1

    for key, value in flag.items():
        assert bug.flags[0][key] == value
