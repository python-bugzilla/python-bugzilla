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
import shutil
import tempfile

import tests
import tests.mockbackend
import tests.utils


def test_tokenfile(monkeypatch):
    dirname = os.path.dirname(__file__)
    monkeypatch.setitem(os.environ, "HOME", dirname + "/data/homedir")

    bz = tests.mockbackend.make_bz(bz_kwargs={"use_creds": True})
    token = dirname + "/data/homedir/.cache/python-bugzilla/bugzillatoken"

    assert token == bz.tokenfile
    del(bz.tokenfile)
    assert bz.tokenfile is None
    assert bz.cookiefile is None


def test_readconfig():
    # Testing for bugzillarc handling
    bzapi = tests.mockbackend.make_bz(version="4.4.0", rhbz=True)
    bzapi.url = "example.com"
    temp = tempfile.NamedTemporaryFile(mode="w")

    def _check(user, password, api_key, cert):
        assert bzapi.user == user
        assert bzapi.password == password
        assert bzapi.api_key == api_key
        assert bzapi.cert == cert

    def _write(c):
        temp.seek(0)
        temp.write(c)
        temp.flush()
        return temp.name

    # Check readconfig normal usage
    content = """
[example.com]
foo=1
user=test1
password=test2
api_key=123abc
cert=/a/b/c
someunknownkey=someval
"""
    bzapi.readconfig(_write(content))
    _check("test1", "test2", "123abc", "/a/b/c")

    # Check loading a different URL, that values aren't overwritten
    content = """
[foo.example.com]
user=test3
password=test4
api_key=567abc
cert=/newpath
"""
    bzapi.readconfig(_write(content))
    _check("test1", "test2", "123abc", "/a/b/c")

    # Change URL, but check readconfig with overwrite=False
    bzapi.url = "foo.example.com"
    bzapi.readconfig(temp.name, overwrite=False)
    _check("test1", "test2", "123abc", "/a/b/c")

    # With default overwrite=True, values will be updated
    # Alter the config to have a / in the hostname, which hits different code
    content = content.replace("example.com", "example.com/xmlrpc.cgi")
    bzapi.url = "https://foo.example.com/xmlrpc.cgi"
    bzapi.readconfig(_write(content))
    _check("test3", "test4", "567abc", "/newpath")

    # Confirm nothing overwritten for a totally different URL
    bzapi.user = None
    bzapi.password = None
    bzapi.api_key = None
    bzapi.cert = None
    bzapi.url = "bugzilla.redhat.com"
    bzapi.readconfig(temp.name)
    _check(None, None, None, None)

    # Test confipath overwrite
    assert [temp.name] == bzapi.configpath
    del(bzapi.configpath)
    assert [] == bzapi.configpath
    bzapi.readconfig()
    _check(None, None, None, None)


def test_authfiles_saving(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    try:
        monkeypatch.setitem(os.environ, "HOME", tmpdir)

        bzapi = tests.mockbackend.make_bz(
            bz_kwargs={"use_creds": True, "cert": "foo-fake-cert"})
        bzapi.connect("https://example.com/fakebz")

        bzapi.cert = "foo-fake-path"
        backend = bzapi._backend  # pylint: disable=protected-access
        bsession = backend._bugzillasession  # pylint: disable=protected-access
        btokencache = bzapi._tokencache   # pylint: disable=protected-access

        # token testing, with repetitions to hit various code paths
        btokencache.set_value(bzapi.url, None)
        assert "Bugzilla_token" not in bsession.get_auth_params()
        btokencache.set_value(bzapi.url, "MY-FAKE-TOKEN")
        assert bsession.get_auth_params()["Bugzilla_token"] == "MY-FAKE-TOKEN"
        btokencache.set_value(bzapi.url, "MY-FAKE-TOKEN")
        btokencache.set_value(bzapi.url, None)
        assert "Bugzilla_token" not in bsession.get_auth_params()
        btokencache.set_value(bzapi.url, "MY-FAKE-TOKEN")

        dirname = os.path.dirname(__file__) + "/data/authfiles/"
        output_token = dirname + "output-token.txt"
        tests.utils.diff_compare(open(bzapi.tokenfile).read(), output_token)

        # Make sure file can re-read them and not error
        bzapi = tests.mockbackend.make_bz(
            bz_kwargs={"use_creds": True,
                       "tokenfile": output_token})
        assert bzapi.tokenfile == output_token

        # Test rcfile writing for api_key
        rcfile = bzapi._rcfile  # pylint: disable=protected-access
        bzapi.url = "https://example.com/fake"
        rcfile.save_api_key(bzapi.url, "TEST-API-KEY")
        rcfilepath = tmpdir + "/.config/python-bugzilla/bugzillarc"
        assert rcfile.get_configpaths()[-1] == rcfilepath
        tests.utils.diff_compare(open(rcfilepath).read(),
            dirname + "output-bugzillarc.txt")

        # Use that generated rcfile to test default URL lookup
        fakeurl = "http://foo.bar.baz/wibble"
        open(rcfilepath, "w").write("\n[DEFAULT]\nurl = %s" % fakeurl)
        assert bzapi.get_rcfile_default_url() == fakeurl
    finally:
        shutil.rmtree(tmpdir)


def test_authfiles_nowrite():
    # Setting values tokenfile is None, should be fine
    bzapi = tests.mockbackend.make_bz(bz_kwargs={"use_creds": False})
    bzapi.connect("https://example.com/foo")
    btokencache = bzapi._tokencache   # pylint: disable=protected-access
    rcfile = bzapi._rcfile  # pylint: disable=protected-access

    btokencache.set_value(bzapi.url, "NEW-TOKEN-VALUE")
    assert rcfile.save_api_key(bzapi.url, "fookey") is None
