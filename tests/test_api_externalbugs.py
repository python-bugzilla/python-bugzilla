#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Test miscellaneous API bits
"""

import tests
import tests.mockbackend


def test_externalbugs():
    # Basic API testing of the ExternalBugs wrappers
    fakebz = tests.mockbackend.make_bz(
        externalbugs_add_args="data/mockargs/test_externalbugs_add.txt",
        externalbugs_add_return={},
        externalbugs_update_args="data/mockargs/test_externalbugs_update.txt",
        externalbugs_update_return={},
        externalbugs_remove_args="data/mockargs/test_externalbugs_remove.txt",
        externalbugs_remove_return={})

    fakebz.add_external_tracker(
        bug_ids=[1234, 5678],
        ext_bz_bug_id="externalid",
        ext_type_id="launchpad",
        ext_type_description="some-bug-add-description",
        ext_type_url="https://example.com/launchpad/1234",
        ext_status="CLOSED",
        ext_description="link to launchpad",
        ext_priority="bigly")

    fakebz.update_external_tracker(
        ids=["external1", "external2"],
        ext_bz_bug_id="externalid-update",
        ext_type_id="mozilla",
        ext_type_description="some-bug-update",
        ext_type_url="https://mozilla.foo/bar/5678",
        ext_status="OPEN",
        bug_ids=["some", "bug", "id"],
        ext_description="link to mozilla",
        ext_priority="like, really bigly")

    fakebz.remove_external_tracker(
        ids="remove1",
        ext_bz_bug_id="99999",
        ext_type_id="footype",
        ext_type_description="foo-desc",
        ext_type_url="foo-url",
        bug_ids="blah")
