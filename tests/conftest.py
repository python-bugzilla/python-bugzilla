# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import locale
import logging
import os
import re

import pytest
import responses

import tests
import tests.utils

import bugzilla


# pytest plugin adding custom options. Hooks are documented here:
# https://docs.pytest.org/en/latest/writing_plugins.html

def pytest_addoption(parser):
    parser.addoption("--ro-integration", action="store_true", default=False,
                     help="Run readonly tests against local Bugzilla instance.")
    parser.addoption("--rw-integration", action="store_true", default=False,
                     help="Run read-write tests against local Bugzilla instance.")
    parser.addoption("--ro-functional", action="store_true", default=False,
            help=("Run readonly functional tests against actual "
                  "bugzilla instances. This will be very slow."))
    parser.addoption("--rw-functional", action="store_true", default=False,
            help=("Run read/write functional tests against actual bugzilla "
                  "instances. As of now this only runs against "
                  "bugzilla.stage.redhat.com, which requires an RH "
                  "bugzilla account with cached login creds. This will "
                  "also be very slow."))
    parser.addoption("--redhat-url",
            help="Redhat bugzilla URL to use for ro/rw_functional tests")
    parser.addoption("--pybz-debug", action="store_true", default=False,
            help=("Enable python-bugzilla debug output. This may break "
                  "output comparison tests."))
    parser.addoption("--regenerate-output",
            action="store_true", default=False,
            help=("Force regeneration of generated test output"))
    parser.addoption("--only-rest", action="store_true", default=False)
    parser.addoption("--only-xmlrpc", action="store_true", default=False)


def pytest_ignore_collect(collection_path, config):
    has_ro = config.getoption("--ro-functional")
    has_ro_i = config.getoption("--ro-integration")
    has_rw = config.getoption("--rw-functional")
    has_rw_i = config.getoption("--rw-integration")

    base = os.path.basename(str(collection_path))
    is_ro = base == "test_ro_functional.py"
    is_ro_i = "tests/integration/ro" in str(collection_path)
    is_rw = base == "test_rw_functional.py"
    is_rw_i = "tests/integration/rw" in str(collection_path)

    if is_ro_i and not has_ro_i:
        return True
    if is_rw_i and not has_rw_i:
        return True

    if is_ro and not has_ro:
        return True
    if is_rw and not has_rw:
        return True


def pytest_configure(config):
    # Needed for test reproducibility on any system not using a UTF-8 locale
    locale.setlocale(locale.LC_ALL, "C")
    for loc in ["C.UTF-8", "C.utf8", "UTF-8", "en_US.UTF-8"]:
        try:
            locale.setlocale(locale.LC_CTYPE, loc)
            break
        except locale.Error:
            pass
    else:
        raise locale.Error("No UTF-8 locale found")

    if config.getoption("--redhat-url"):
        tests.CLICONFIG.REDHAT_URL = config.getoption("--redhat-url")
    if config.getoption("--pybz-debug"):
        logging.getLogger(bugzilla.__name__).setLevel(logging.DEBUG)
        os.environ["__BUGZILLA_UNITTEST_DEBUG"] = "1"
    if config.getoption("--regenerate-output"):
        tests.CLICONFIG.REGENERATE_OUTPUT = config.getoption(
            "--regenerate-output")
    if config.getoption("--only-rest"):
        tests.CLICONFIG.ONLY_REST = True
    if config.getoption("--only-xmlrpc"):
        tests.CLICONFIG.ONLY_XMLRPC = True

    if (config.getoption("--ro-functional") or
        config.getoption("--rw-functional")):
        config.option.verbose = 2


def pytest_generate_tests(metafunc):
    """
    If a test requests the 'backends' fixture, run that test with both
    force_rest=True and force_xmlrpc=True Bugzilla options
    """
    if 'backends' in metafunc.fixturenames:
        values = []
        ids = []
        if not tests.CLICONFIG.ONLY_REST:
            values.append({"force_xmlrpc": True})
            ids.append("XMLRPC")
        if not tests.CLICONFIG.ONLY_XMLRPC:
            values.append({"force_rest": True})
            ids.append("REST")
        metafunc.parametrize("backends", values, ids=ids, scope="session")


@pytest.fixture
def run_cli(capsys, monkeypatch):
    """
    Custom pytest fixture to pass a function for testing
    a bugzilla cli command.
    """
    def _do_run(*args, **kwargs):
        return tests.utils.do_run_cli(capsys, monkeypatch, *args, **kwargs)
    return _do_run


@pytest.fixture
def mocked_responses():
    """
    Mock responses

    * Quickly return error responses
    * Pass through requests to live instances
    * Provide an incorrect XMLRPC response
    """
    passthrough = ()
    status_pattern = re.compile(r"https://httpstat.us/(?P<status>\d+).*")

    def status_callback(request):
        match = status_pattern.match(request.url)
        status_code = 400
        if match:
            status_code = int(match.group("status"))

        return status_code, {}, "<html><body><h1>Lorem ipsum</h1></body></html>"

    test_url = os.getenv("BUGZILLA_URL")
    if test_url:
        passthrough += (test_url, test_url.replace("http://", "https://"))
    with responses.RequestsMock(passthru_prefixes=passthrough,
                                assert_all_requests_are_fired=False) as mock:
        mock.add_callback(
            method=responses.GET,
            url=status_pattern,
            callback=status_callback
        )
        mock.add_callback(
            method=responses.POST,
            url=status_pattern,
            callback=status_callback
        )
        mock.add(
            method=responses.POST,
            url="https://example.com/#xmlrpc",
            status=200,
            body="This is no XML"
        )
        yield mock
