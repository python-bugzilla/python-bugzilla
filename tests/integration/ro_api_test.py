# Ignoring pytest-related warnings:
# pylint: disable=redefined-outer-name,unused-argument
import pytest

from bugzilla import BugzillaError

from ..utils import open_bz
from . import TEST_URL, TEST_PRODUCTS, TEST_SUSE_COMPONENTS, TEST_OWNER


def test_rest_xmlrpc_detection(mocked_responses):
    # The default: use XMLRPC
    bz = open_bz(url=TEST_URL)
    assert bz.is_xmlrpc()
    assert "/xmlrpc.cgi" in bz.url

    # See /rest in the URL, so use REST
    bz = open_bz(url=TEST_URL + "/rest")
    assert bz.is_rest()
    with pytest.raises(BugzillaError) as e:
        dummy = bz._proxy  # pylint: disable=protected-access
    assert "raw XMLRPC access is not provided" in str(e)

    # See /xmlrpc.cgi in the URL, so use XMLRPC
    bz = open_bz(url=TEST_URL + "/xmlrpc.cgi")
    assert "/xmlrpc.cgi" in bz.url
    assert bz.is_xmlrpc()
    assert bz._proxy  # pylint: disable=protected-access


def test_apikey_error_scraping(mocked_responses):
    # Ensure the API key does not leak into any requests exceptions
    fakekey = "FOOBARMYKEY"
    with pytest.raises(Exception) as e:
        open_bz("https://httpstat.us/400&foo",
                force_xmlrpc=True, api_key=fakekey)
    assert "Client Error" in str(e.value)
    assert fakekey not in str(e.value)

    with pytest.raises(Exception) as e:
        open_bz("https://httpstat.us/400&foo",
                force_rest=True, api_key=fakekey)
    assert "Client Error" in str(e.value)
    assert fakekey not in str(e.value)


def test_xmlrpc_bad_url(mocked_responses):
    with pytest.raises(BugzillaError) as e:
        open_bz(url="https://example.com/#xmlrpc", force_xmlrpc=True)
    assert "URL may not be an XMLRPC URL" in str(e)


def test_get_products(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)

    assert len(bz.products) == 3
    assert {p["name"] for p in bz.products} == TEST_PRODUCTS

    rhel = next(p for p in bz.products if p["id"] == 2)
    assert {v["name"] for v in rhel["versions"]} == {"9.0", "9.1", "unspecified"}


def test_get_components(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    components = bz.getcomponents(product="SUSE Linux Enterprise Server 15 SP6")
    assert len(components) == 2
    assert set(components) == TEST_SUSE_COMPONENTS


def test_get_component_detail(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    component = bz.getcomponentdetails(product="Red Hat Enterprise Linux 9",
                                       component="python-bugzilla")
    assert component["id"] == 2
    assert component["default_assigned_to"] == TEST_OWNER


def test_query(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    query = bz.build_query(product="Red Hat Enterprise Linux 9", component="python-bugzilla")
    bugs = bz.query(query=query)

    assert len(bugs) == 1
    assert bugs[0].id == 2
    assert bugs[0].summary == "Expect the Spanish inquisition"

    bz = open_bz(url=TEST_URL, **backends)
    query = bz.build_query(product="SUSE Linux Enterprise Server 15 SP6")
    bugs = bz.query(query=query)

    assert len(bugs) == 1
    assert bugs[0].id == 1
    assert bugs[0].whiteboard == "AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L"


def test_get_bug_alias(mocked_responses, backends):
    bz = open_bz(url=TEST_URL, **backends)
    bug = bz.getbug("FOO-1")

    assert bug.id == 1
    assert bug.summary == "ZeroDivisionError in function foo_bar()"