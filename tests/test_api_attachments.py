# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

import os

import pytest

import tests
import tests.mockbackend


def test_api_attachments():
    # misc coverage testing for Bugzilla attachment APIs
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_get_all_args=(
            "data/mockargs/test_attachments_getall1.txt"),
        bug_attachment_get_all_return={},
        bug_attachment_update_args=(
            "data/mockargs/test_attachments_update1.txt"),
        bug_attachment_update_return={},
        bug_attachment_get_args=(
            "data/mockargs/test_attachments_get1.txt"),
        bug_attachment_get_return=(
            "data/mockreturn/test_attach_get1.txt"),
        bug_attachment_create_args=(
            "data/mockargs/test_api_attachments_create1.txt"),
        bug_attachment_create_return={
            "attachments": {"123456": {}, "456789": []}},
    )

    # coverage for include/exclude handling
    fakebz.get_attachments([123456], None,
            include_fields=["foo"], exclude_fields="bar")

    # coverage for updateattachment
    fakebz.updateattachmentflags(None, "112233", "needinfo",
            value="foobar", is_patch=True)

    # coverage for openattachment
    fobj = fakebz.openattachment(502352)
    assert "Hooray" in str(fobj.read())

    # Error on bad input type
    with pytest.raises(TypeError):
        fakebz.attachfile([123456], None, "some desc")

    # Misc attachfile() pieces
    attachfile = os.path.dirname(__file__) + "/data/bz-attach-get1.txt"
    ret = fakebz.attachfile([123456], attachfile, "some desc",
            isprivate=True)
    ret.sort()
    assert ret == [123456, 456789]
