# Ignoring pytest-related warnings:
# pylint: disable=unused-argument
from ..utils import open_bz
from . import TEST_URL, TEST_PRODUCTS, TEST_SUSE_COMPONENTS, TEST_OWNER


def test_get_products(mocked_responses, run_cli, backends):
    bz = open_bz(url=TEST_URL, **backends)
    out = run_cli("bugzilla info --products", bzinstance=bz)
    assert len(out.strip().split("\n")) == 3

    for product in TEST_PRODUCTS:
        assert product in out


def test_get_components(mocked_responses, run_cli, backends):
    bz = open_bz(url=TEST_URL, **backends)
    out = run_cli("bugzilla info --components 'SUSE Linux Enterprise Server 15 SP6'", bzinstance=bz)
    assert len(out.strip().split("\n")) == 2
    for comp in TEST_SUSE_COMPONENTS:
        assert comp in out


def test_get_component_owners(mocked_responses, run_cli, backends):
    bz = open_bz(url=TEST_URL, **backends)
    out = run_cli("bugzilla info --component_owners 'SUSE Linux Enterprise Server 15 SP6'",
                  bzinstance=bz)
    assert TEST_OWNER in out


def test_get_versions(mocked_responses, run_cli, backends):
    bz = open_bz(url=TEST_URL, **backends)
    out = run_cli("bugzilla info --versions 'Red Hat Enterprise Linux 9'", bzinstance=bz)
    versions = set(out.strip().split("\n"))

    assert versions == {"unspecified", "9.0", "9.1"}


def test_query(mocked_responses, run_cli, backends):
    bz = open_bz(url=TEST_URL, **backends)
    out = run_cli("bugzilla query --product 'Red Hat Enterprise Linux 9' "
                  "--component 'python-bugzilla'", bzinstance=bz)
    lines = out.strip().splitlines()

    assert len(lines) == 1
    assert lines[0].startswith("#2")
    assert "Expect the Spanish inquisition" in lines[0]
