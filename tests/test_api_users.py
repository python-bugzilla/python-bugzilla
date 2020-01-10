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


def test_api_users():
    # Basic API testing of the users APIs
    user_ret = {'users': [
        {'can_login': True,
         'email': 'example1@example.com',
         'id': 1010101,
         'name': 'example1@example.com',
         'real_name': 'Mr. Example Man'},
        {'can_login': False,
         'email': 'example2@example.com',
         'id': 2222333,
         'name': 'example name',
         'real_name': 'Example real name',
         'saved_reports': [],
         'saved_searches': [],
         'groups': [
             {"id": 1, "name": "testgroup", "description": "somedesc"}
         ]},
    ]}

    # getusers and User testing
    fakebz = tests.mockbackend.make_bz(
        user_get_args="data/mockargs/test_api_users_get1.txt",
        user_get_return=user_ret,
        user_update_args="data/mockargs/test_api_users_update1.txt",
        user_update_return={})
    userobj = fakebz.getuser("example2@example.com")

    # Some userobj testing
    userobj.refresh()
    assert userobj.userid == 2222333
    assert userobj.email == "example2@example.com"
    assert userobj.name == "example name"
    assert userobj.can_login is False
    userobj.updateperms("rem", ["fedora_contrib"])

    # Catch a validation error
    with pytest.raises(bugzilla.BugzillaError):
        userobj.updateperms("badaction", ["newgroup"])

    # createuser tests
    fakebz = tests.mockbackend.make_bz(
        user_get_args="data/mockargs/test_api_users_get2.txt",
        user_get_return=user_ret,
        user_create_args="data/mockargs/test_api_users_create.txt",
        user_create_return={})
    userobj = fakebz.createuser("example1@example.com", "fooname", "foopass")
    assert userobj.email == "example1@example.com"


    # searchuser tests
    fakebz = tests.mockbackend.make_bz(
        user_get_args="data/mockargs/test_api_users_get3.txt",
        user_get_return=user_ret)
    userlist = fakebz.searchusers("example1@example.com")
    assert len(userlist) == 2
