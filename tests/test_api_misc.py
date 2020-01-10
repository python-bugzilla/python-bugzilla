#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Test miscellaneous API bits
"""

import sys
import tempfile

import pytest

import bugzilla

import tests
import tests.mockbackend


def test_mock_rhbz():
    fakebz = tests.mockbackend.make_bz(rhbz=True)
    assert fakebz.__class__ == bugzilla.RHBugzilla


def testUserAgent():
    b3 = tests.mockbackend.make_bz(version="3.0.0")
    assert "python-bugzilla" in b3.user_agent


def test_fixurl():
    assert (bugzilla.Bugzilla.fix_url("example.com") ==
        "https://example.com/xmlrpc.cgi")
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


def testSubComponentFail():
    bz = tests.mockbackend.make_bz(version="4.4.0", rhbz=True)
    with pytest.raises(ValueError):
        bz.build_update(sub_component="some sub component")


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

    # Will log in immediately, hitting basic_auth path
    bz = tests.mockbackend.make_bz(
        bz_kwargs={"basic_auth": True, "user": "FOO", "password": "BAR"},
        user_login_args="data/mockargs/test_api_login1.txt",
        user_login_return={})

    # Hit default api_key code path
    bz = tests.mockbackend.make_bz(
        bz_kwargs={"api_key": "FAKE_KEY"},
        user_login_args="data/mockargs/test_api_login.txt",
        user_login_return={})
    # Try reconnect, with RHBZ testing
    bz.connect("https:///fake/bugzilla.redhat.com")
    bz.connect()


def test_interactive_login(capsys, monkeypatch):
    bz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_interactive_login.txt",
        user_login_return={},
        user_logout_args=None,
        user_logout_return={},
        user_get_args=None,
        user_get_return={})

    tests.utils.monkeypatch_getpass(monkeypatch)

    fakestdin = tests.utils.fake_stream("fakeuser\nfakepass\n")
    monkeypatch.setattr(sys, "stdin", fakestdin)
    bz.interactive_login()
    bz.logout()

    out = capsys.readouterr()[0]
    assert "Bugzilla Username:" in out
    assert "Bugzilla Password:" in out

    # API key prompting and saving
    tmp = tempfile.NamedTemporaryFile()
    bz.configpath = [tmp.name]
    bz.url = "https://example.com"

    fakestdin = tests.utils.fake_stream("MY-FAKE-KEY\n")
    monkeypatch.setattr(sys, "stdin", fakestdin)
    bz.interactive_login(use_api_key=True)
    out = capsys.readouterr()[0]
    assert "API Key:" in out
    assert tmp.name in out
    tests.utils.diff_compare(open(tmp.name).read(),
            "data/clioutput/test_interactive_login_apikey_rcfile.txt")


def test_version_bad():
    # Hit version error handling
    bz = tests.mockbackend.make_bz(version="badversion")
    assert bz.bz_ver_major == 5
    assert bz.bz_ver_minor == 0

    # pylint: disable=protected-access
    assert bz._check_version(5, 0)
    assert not bz._check_version(10000, 0)


def test_extensions_bad():
    # Hit bad extensions error handling
    tests.mockbackend.make_bz(extensions="BADEXTENSIONS")


def test_bad_scheme():
    bz = tests.mockbackend.make_bz()
    try:
        bz.connect("ftp://example.com")
    except Exception as e:
        assert "Invalid URL scheme: ftp" in str(e)
