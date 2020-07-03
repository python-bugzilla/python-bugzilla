#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Test miscellaneous API bits
"""

import pytest

import bugzilla

import tests
import tests.mockbackend


def test_mock_rhbz():
    fakebz = tests.mockbackend.make_bz(rhbz=True)
    assert fakebz.__class__ == bugzilla.RHBugzilla


def test_file_imports():
    # Ensure historically stable import paths continue to work
    # pylint: disable=unused-import
    from bugzilla.rhbugzilla import RHBugzilla
    from bugzilla.bug import Bug
    from bugzilla.base import Bugzilla


def testUserAgent():
    b3 = tests.mockbackend.make_bz(version="3.0.0")
    assert "python-bugzilla" in b3.user_agent


def test_fixurl():
    assert (bugzilla.Bugzilla.fix_url("example.com") ==
        "https://example.com/xmlrpc.cgi")
    assert (bugzilla.Bugzilla.fix_url("example.com", force_rest=True) ==
        "https://example.com/rest/")
    assert (bugzilla.Bugzilla.fix_url("example.com/xmlrpc.cgi") ==
        "https://example.com/xmlrpc.cgi")
    assert (bugzilla.Bugzilla.fix_url("http://example.com/somepath.cgi") ==
        "http://example.com/somepath.cgi")


def testPostTranslation():
    def _testPostCompare(bz, indict, outexpect):
        outdict = indict.copy()
        bz.post_translation({}, outdict)
        assert outdict == outexpect

        # Make sure multiple calls don't change anything
        bz.post_translation({}, outdict)
        assert outdict == outexpect

    bug3 = tests.mockbackend.make_bz(version="3.4.0")
    rhbz = tests.mockbackend.make_bz(version="4.4.0", rhbz=True)

    test1 = {
        "component": ["comp1"],
        "version": ["ver1", "ver2"],

        'flags': [{
            'is_active': 1,
            'name': 'qe_test_coverage',
            'setter': 'pm-rhel@redhat.com',
            'status': '?',
        }, {
            'is_active': 1,
            'name': 'rhel-6.4.0',
            'setter': 'pm-rhel@redhat.com',
            'status': '+',
        }],

        'alias': ["FOO", "BAR"],
        'blocks': [782183, 840699, 923128],
        'keywords': ['Security'],
        'groups': ['redhat'],
    }

    out_simple = test1.copy()
    out_simple["components"] = out_simple["component"]
    out_simple["component"] = out_simple["components"][0]
    out_simple["versions"] = out_simple["version"]
    out_simple["version"] = out_simple["versions"][0]

    _testPostCompare(bug3, test1, test1)
    _testPostCompare(rhbz, test1, out_simple)


def test_rhbz_pre_translation():
    bz = tests.mockbackend.make_bz(rhbz=True)
    input_query = {
        "bug_id": "12345,6789",
        "component": "comp1,comp2",
        "column_list": ["field1", "field8"],
    }

    bz.pre_translation(input_query)
    output_query = {
        'component': ['comp1', 'comp2'],
        'id': ['12345', '6789'],
        'include_fields': ['field1', 'field8', 'id'],
    }

    assert output_query == input_query


def testUpdateFailures():
    # sub_component without component also passed
    bz = tests.mockbackend.make_bz(version="4.4.0", rhbz=True)
    with pytest.raises(ValueError):
        bz.build_update(sub_component="some sub component")

    # Trying to update value that only rhbz supports
    bz = tests.mockbackend.make_bz()
    with pytest.raises(ValueError):
        bz.build_update(fixed_in="some fixedin value")


def testCreatebugFieldConversion():
    bz4 = tests.mockbackend.make_bz(version="4.0.0")
    vc = bz4._validate_createbug  # pylint: disable=protected-access
    out = vc(product="foo", component="bar",
        version="12", description="foo", short_desc="bar",
        check_args=False)
    assert out == {
        'component': 'bar', 'description': 'foo', 'product': 'foo',
        'summary': 'bar', 'version': '12'}


def testURLSavedSearch():
    bz4 = tests.mockbackend.make_bz(version="4.0.0")
    url = ("https://bugzilla.redhat.com/buglist.cgi?"
        "cmdtype=dorem&list_id=2342312&namedcmd="
        "RHEL7%20new%20assigned%20virt-maint&remaction=run&"
        "sharer_id=321167")
    query = {
        'sharer_id': '321167',
        'savedsearch': 'RHEL7 new assigned virt-maint'
    }
    assert bz4.url_to_query(url) == query


def testStandardQuery():
    bz4 = tests.mockbackend.make_bz(version="4.0.0")
    url = ("https://bugzilla.redhat.com/buglist.cgi?"
        "component=virt-manager&query_format=advanced&classification="
        "Fedora&product=Fedora&bug_status=NEW&bug_status=ASSIGNED&"
        "bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&"
        "bug_status=VERIFIED&bug_status=FAILS_QA&bug_status="
        "RELEASE_PENDING&bug_status=POST&order=bug_status%2Cbug_id")
    query = {
        'product': 'Fedora',
        'query_format': 'advanced',
        'bug_status': ['NEW', 'ASSIGNED', 'MODIFIED', 'ON_DEV',
            'ON_QA', 'VERIFIED', 'FAILS_QA', 'RELEASE_PENDING', 'POST'],
        'classification': 'Fedora',
        'component': 'virt-manager',
        'order': 'bug_status,bug_id'
    }
    assert bz4.url_to_query(url) == query

    # Test with unknown URL
    assert bz4.url_to_query("https://example.com") == {}


def test_api_login():
    with pytest.raises(TypeError):
        # Missing explicit URL
        bugzilla.Bugzilla()

    with pytest.raises(Exception):
        # Calling connect() with passed in URL
        bugzilla.Bugzilla(url="https:///FAKEURL")

    bz = tests.mockbackend.make_bz()

    with pytest.raises(ValueError):
        # Errors on missing user
        bz.login()

    bz.user = "FOO"
    with pytest.raises(ValueError):
        # Errors on missing pass
        bz.login()

    bz.password = "BAR"
    bz.api_key = "WIBBLE"
    with pytest.raises(ValueError):
        # Errors on api_key + login()
        bz.login()

    # Hit default api_key code path
    bz = tests.mockbackend.make_bz(
        bz_kwargs={"api_key": "FAKE_KEY"},
        user_login_args="data/mockargs/test_api_login.txt",
        user_login_return={})
    # Try reconnect, with RHBZ testing
    bz.connect("https:///fake/bugzilla.redhat.com")
    bz.connect()

    # Test auto login if user/password is set
    bz = tests.mockbackend.make_bz(
        bz_kwargs={"user": "FOO", "password": "BAR"},
        user_login_args="data/mockargs/test_api_login2.txt",
        user_login_return={},
        user_logout_args=None,
        user_logout_return={})

    # Test logout
    bz.logout()


def test_version_bad():
    # Hit version error handling
    bz = tests.mockbackend.make_bz(version="badversion")
    assert bz.bz_ver_major == 5
    assert bz.bz_ver_minor == 0

    # pylint: disable=protected-access
    assert bz._get_version() == 5.0


def test_extensions_bad():
    # Hit bad extensions error handling
    tests.mockbackend.make_bz(extensions="BADEXTENSIONS")


def test_bad_scheme():
    bz = tests.mockbackend.make_bz()
    try:
        bz.connect("ftp://example.com")
    except Exception as e:
        assert "Invalid URL scheme: ftp" in str(e)


def test_update_flags():
    # update_flags is just a compat wrapper for update_bugs
    bz = tests.mockbackend.make_bz(
        bug_update_args="data/mockargs/test_update_flags.txt",
        bug_update_return={})
    bz.update_flags([12345, 6789], {"name": "needinfo", "status": "?"})


def test_bugs_history_raw():
    # Stub test for bugs_history_raw
    ids = ["12345", 567]
    bz = tests.mockbackend.make_bz(
        bug_history_args=(ids, {}),
        bug_history_return={})
    bz.bugs_history_raw(ids)


def test_get_comments():
    # Stub test for get_commands
    ids = ["12345", 567]
    bz = tests.mockbackend.make_bz(
        bug_comments_args=(ids, {}),
        bug_comments_return={})
    bz.get_comments(ids)


def test_get_xmlrpc_proxy():
    # Ensure _proxy goes to a backend API
    bz = tests.mockbackend.make_bz()
    with pytest.raises(NotImplementedError):
        dummy = bz._proxy  # pylint: disable=protected-access

    assert bz.is_xmlrpc() is False
    assert bz.is_rest() is False
    assert hasattr(bz.get_requests_session(), "request")


def test_requests_session_passthrough():
    import requests
    session = requests.Session()

    bz = tests.mockbackend.make_bz(
        bz_kwargs={"requests_session": session, "sslverify": False})
    assert bz.get_requests_session() is session
    assert session.verify is False


def test_query_url_fail():
    # test some handling of query from_url errors
    query = {"query_format": "advanced", "product": "FOO"}
    checkstr = "does not appear to support"

    exc = bugzilla.BugzillaError("FAKEERROR query_format", code=123)
    bz = tests.mockbackend.make_bz(version="4.0.0",
        bug_search_args=None, bug_search_return=exc)
    try:
        bz.query(query)
    except Exception as e:
        assert checkstr in str(e)

    bz = tests.mockbackend.make_bz(version="5.1.0",
        bug_search_args=None, bug_search_return=exc)
    try:
        bz.query(query)
    except Exception as e:
        assert checkstr not in str(e)
