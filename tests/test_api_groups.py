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


def test_api_groups():
    # Basic API testing of the users APIs
    group_ret = {"groups": [{
        "membership": [
            {"real_name": "Bugzilla User",
            "can_login": 1,
            "name": "user@bugzilla.org",
            "login_denied_text": "",
            "id": 85,
            "email_enabled": 1,
            "email": "user@bugzilla.org"},
            {"real_name": "Bugzilla User2",
            "can_login": 0,
            "name": "user2@bugzilla.org",
            "login_denied_text": "",
            "id": 77,
            "email_enabled": 0,
            "email": "user2@bugzilla.org"},
        ],
        "is_active": 1,
        "description": "Test Group",
        "user_regexp": "",
        "is_bug_group": 1,
        "name": "TestGroup",
        "id": 9
    }]}

    fakebz = tests.mockbackend.make_bz(
        group_get_args="data/mockargs/test_api_groups_get1.txt",
        group_get_return=group_ret)

    # getgroups testing
    groupobj = fakebz.getgroups("TestGroups")[0]
    assert groupobj.groupid == 9
    assert groupobj.member_emails == [
        "user2@bugzilla.org", "user@bugzilla.org"]
    assert groupobj.name == "TestGroup"

    # getgroup testing
    fakebz = tests.mockbackend.make_bz(
        group_get_args="data/mockargs/test_api_groups_get2.txt",
        group_get_return=group_ret)
    groupobj = fakebz.getgroup("TestGroup", membership=True)
    groupobj.membership = []
    assert groupobj.members() == group_ret["groups"][0]["membership"]
