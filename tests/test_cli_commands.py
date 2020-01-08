# -*- coding: utf-8 -*-

# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import os
import re

import pytest

import bugzilla

import tests
import tests.mockbackend
import tests.utils


#################################
# 'bugzilla login' mock testing #
#################################

def test_login(run_cli):
    cmd = "bugzilla login FOO BAR"

    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login.txt",
        user_login_return=RuntimeError("TEST ERROR"))
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "Login failed: TEST ERROR" in out

    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={})
    out = run_cli(cmd, fakebz)
    assert "Login successful" in out

    cmd = "bugzilla --restrict-login --user FOO --password BAR login"
    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login-restrict.txt",
        user_login_return={})
    out = run_cli(cmd, fakebz)
    assert "Login successful" in out

    cmd = "bugzilla --ensure-logged-in --user FOO --password BAR login"
    # Raises raw error trying to see if we aren't logged in
    with pytest.raises(NotImplementedError):
        fakebz = tests.mockbackend.make_bz(
            user_login_args="data/mockargs/test_login.txt",
            user_login_return={},
            user_get_args=None,
            user_get_return=NotImplementedError())
        out = run_cli(cmd, fakebz)

    # Errors with expected code
    cmd = "bugzilla --ensure-logged-in --user FOO --password BAR login"
    fakebz = tests.mockbackend.make_bz(
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={},
        user_get_args=None,
        user_get_return=bugzilla.BugzillaError("TESTMESSAGE", code=505))
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "--ensure-logged-in passed but you" in out

    # Returns success for logged_in check and hits a tokenfile line
    cmd = "bugzilla --ensure-logged-in "
    cmd += "--user FOO --password BAR login"
    fakebz = tests.mockbackend.make_bz(
        bz_kwargs={"use_creds": True},
        user_login_args="data/mockargs/test_login.txt",
        user_login_return={},
        user_get_args=None,
        user_get_return={})
    out = run_cli(cmd, fakebz)
    assert "token cache updated" in out


################################
# 'bugzilla info' mock testing #
################################

def test_info(run_cli):
    funcname = tests.utils.get_funcname()
    argsprefix = "data/mockargs/%s_" % funcname
    cliprefix = "data/clioutput/%s_" % funcname

    prod_accessible = {'ids': [1, 7]}
    prod_get = {'products': [
        {'id': 1, 'name': 'Prod 1 Test'},
        {'id': 7, 'name': 'test-fake-product'}
    ]}

    # info --products
    fakebz = tests.mockbackend.make_bz(
        product_get_accessible_args=None,
        product_get_accessible_return=prod_accessible,
        product_get_args=argsprefix + "products.txt",
        product_get_return=prod_get)
    cmd = "bugzilla info --products"
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, cliprefix + "products.txt")

    # info --versions
    prod_get_ver = {'products': [
        {'id': 7, 'name': 'test-fake-product',
         'versions': [
             {'id': 360, 'is_active': True, 'name': '7.1'},
             {'id': 123, 'is_active': True, 'name': 'fooversion!'},
         ]},
    ]}
    fakebz = tests.mockbackend.make_bz(
        product_get_args=argsprefix + "versions.txt",
        product_get_return=prod_get_ver)
    cmd = "bugzilla info --versions test-fake-product"
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, cliprefix + "versions.txt")

    # info --components
    legal_values = {'values': ["comp1", "test-comp-2", "hey-imma-comp"]}
    cmd = "bugzilla info --components test-fake-product"
    fakebz = tests.mockbackend.make_bz(
        product_get_args=argsprefix + "components.txt",
        product_get_return=prod_get,
        bug_legal_values_args=argsprefix + "components-legalvalues.txt",
        bug_legal_values_return=legal_values)
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, cliprefix + "components.txt")

    # info --components --active-components
    cmd = "bugzilla info --components test-fake-product --active-components"
    prod_get_comp_active = {'products': [
        {'id': 7, 'name': 'test-fake-product',
         'components': [
             {'is_active': True, 'name': 'backend/kernel'},
             {'is_active': True, 'name': 'client-interfaces'},
         ]},
    ]}
    fakebz = tests.mockbackend.make_bz(
        product_get_args=argsprefix + "components-active.txt",
        product_get_return=prod_get_comp_active)
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, cliprefix + "components-active.txt")

    # info --components_owners
    cmd = "bugzilla info --component_owners test-fake-product"
    prod_get_comp_owners = {'products': [
        {'id': 7, 'name': 'test-fake-product',
         'components': [
             {'default_assigned_to': 'Fake Guy',
              'name': 'client-interfaces'},
             {'default_assigned_to': 'ANother fake dude!',
              'name': 'configuration'},
         ]},
    ]}
    fakebz = tests.mockbackend.make_bz(
        product_get_args=argsprefix + "components-owners.txt",
        product_get_return=prod_get_comp_owners)
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, cliprefix + "components-owners.txt")


#################################
# 'bugzilla query' mock testing #
#################################

def test_query(run_cli):
    # query that ends up empty
    cmd = "bugzilla query --ids "
    fakebz = tests.mockbackend.make_bz(version="3.0.0")
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "requires additional arguments" in out

    # bad field option
    cmd = "bugzilla query --field FOO"
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "Invalid field argument" in out

    # Simple query with some comma opts
    cmd = "bugzilla query "
    cmd += "--product foo --component foo,bar --bug_id 1234,2480"
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query1.txt",
        bug_search_return="data/mockreturn/test_query1.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query1.txt")

    # Same but with --ids output
    cmd = "bugzilla query --ids "
    cmd += "--product foo --component foo,bar --bug_id 1234,2480"
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query1-ids.txt",
        bug_search_return="data/mockreturn/test_query1.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query1-ids.txt")

    # Same but with --raw output
    cmd = "bugzilla query --raw --bug_id 1165434"
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query2.txt",
        bug_search_return={"bugs": [{"id": 1165434}]},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    # Dictionary ordering is random, so scrub it from our output
    out = re.sub(r"\{.*\}", r"'DICT SCRUBBED'", out, re.MULTILINE)
    tests.utils.diff_compare(out, "data/clioutput/test_query2.txt")

    # Test a bunch of different combinations for code coverage
    cmd = "bugzilla query --status ALL --severity sev1,sev2 "
    cmd += "--outputformat='%{foo}:%{bar}::%{whiteboard}:"
    cmd += "%{flags}:%{flags_requestee}%{whiteboard:devel}::"
    cmd += "%{flag:needinfo}::%{comments}::%{external_bugs}'"
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query3.txt",
        bug_search_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query3.txt")

    # Test --status DEV and --full
    cmd = "bugzilla query --status DEV --full"
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query4.txt",
        bug_search_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query4.txt")

    # Test --status QE and --extra, and components-file
    compfile = os.path.dirname(__file__) + "/data/components_file.txt"
    cmd = "bugzilla query --status QE --extra "
    cmd += "--components_file %s" % compfile
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query5.txt",
        bug_search_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query5.txt")

    # Test --status EOL and --oneline, and some --field usage
    cmd = "bugzilla query --status EOL --oneline "
    cmd += "--field FOO=1 --field=BAR=WIBBLE "
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query6.txt",
        bug_search_return="data/mockreturn/test_getbug_rhel.txt",
        bug_get_args="data/mockargs/test_query_cve_getbug.txt",
        bug_get_return="data/mockreturn/test_query_cve_getbug.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query6.txt")

    # Test --status OPEN and --from-url
    url = "https://bugzilla.redhat.com/buglist.cgi?bug_status=NEW&bug_status=ASSIGNED&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=FAILS_QA&bug_status=RELEASE_PENDING&bug_status=POST&classification=Fedora&component=virt-manager&order=bug_status%2Cbug_id&product=Fedora&query_format=advanced"  # noqa
    cmd = "bugzilla query --status OPEN --from-url %s" % url
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query7.txt",
        bug_search_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query7.txt")


###############################
# 'bugzilla new' mock testing #
###############################

def test_new(run_cli):
    # Bunch of options
    cmd = "bugzilla new --product FOOPROD --component FOOCOMP "
    cmd += "--summary 'Hey this is the title!' "
    cmd += "--comment 'This is the first comment!\nWith newline & stuff.' "
    cmd += "--keywords ADDKEY --groups FOOGROUP,BARGROUP"

    fakebz = tests.mockbackend.make_bz(
        bug_create_args="data/mockargs/test_new1.txt",
        bug_create_return={"id": 1694158},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_new1.txt")


##################################
# 'bugzilla modify' mock testing #
##################################

def test_modify(run_cli):
    # errors on missing args
    cmd = "bugzilla modify 123456"
    fakebz = tests.mockbackend.make_bz()
    out = run_cli(cmd, fakebz, expectfail=True)
    assert "additional arguments" in out

    # Modify basic
    cmd = "bugzilla modify 123456 1234567 "
    cmd += "--status ASSIGNED --component NEWCOMP "
    fakebz = tests.mockbackend.make_bz(
        bug_update_args="data/mockargs/test_modify1.txt",
        bug_update_return={})
    out = run_cli(cmd, fakebz)
    assert not out

    # Modify with lots of opts
    cmd = "bugzilla modify 123456 --component NEWCOMP "
    cmd += "--keyword +FOO --groups=-BAR --blocked =123456,445566 "
    cmd += "--flag=-needinfo,+somethingelse "
    cmd += "--whiteboard =foo --whiteboard =thisone "
    cmd += "--dupeid 555666 "
    fakebz = tests.mockbackend.make_bz(
        bug_update_args="data/mockargs/test_modify2.txt",
        bug_update_return={})
    out = run_cli(cmd, fakebz)
    assert not out

    # Modify with tricky opts
    cmd = "bugzilla modify 1165434 "
    cmd += "--tags +addtag --tags=-rmtag "
    cmd += "--qa_whiteboard +yo-qa --qa_whiteboard=-foo "
    cmd += "--internal_whiteboard +internal-hey --internal_whiteboard +bar "
    cmd += "--devel_whiteboard +devel-duh --devel_whiteboard=-yay "
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_update_tags_args="data/mockargs/test_modify3-tags.txt",
        bug_update_tags_return={},
        bug_update_args="data/mockargs/test_modify3.txt",
        bug_update_return={},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    assert not out


##################################
# 'bugzilla attach' mock testing #
##################################

def test_attach(run_cli):
    attachfile = os.path.dirname(__file__) + "/data/bz-attach-get1.txt"
    attachcontent = open(attachfile).read()

    # Hit error when no ID specified
    fakebz = tests.mockbackend.make_bz()
    out = run_cli("bugzilla attach", fakebz, expectfail=True)
    assert "ID must be specified" in out

    # Hit error when using tty and no --file specified
    out = run_cli("bugzilla attach 123456", fakebz, expectfail=True)
    assert "--file must be specified" in out

    # Hit error when using stdin, but no --desc
    out = run_cli("bugzilla attach 123456", fakebz, expectfail=True,
            stdin=attachcontent)
    assert "--description must be specified" in out

    # Basic CLI attach
    cmd = "bugzilla attach 123456 --file=%s " % attachfile
    cmd += "--type text/x-patch --private "
    cmd += "--comment 'some comment to go with it'"
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_create_args="data/mockargs/test_attach1.txt",
        bug_attachment_create_return={'ids': [1557949]})
    out = run_cli(cmd, fakebz)
    assert "Created attachment 1557949 on bug 123456" in out

    # Attach from stdin
    cmd = "bugzilla attach 123456 --file=fake-file-name.txt "
    cmd += "--description 'Some attachment description' "
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_create_args="data/mockargs/test_attach2.txt",
        bug_attachment_create_return={'ids': [1557949]})
    out = run_cli(cmd, fakebz, stdin=attachcontent)
    assert "Created attachment 1557949 on bug 123456" in out


def _test_attach_get(run_cli):
    # Hit error when using ids with --get*
    fakebz = tests.mockbackend.make_bz()
    out = run_cli("bugzilla attach 123456 --getall 123456",
            fakebz, expectfail=True)
    assert "not used for" in out

    # Basic --get ATTID usage
    filename = u"Klíč memorial test file.txt"
    cmd = "bugzilla attach --get 112233"
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_get_args="data/mockargs/test_attach_get1.txt",
        bug_attachment_get_return="data/mockreturn/test_attach_get1.txt")
    out = run_cli(cmd, fakebz)
    assert filename in out

    # Basic --getall with --ignore-obsolete
    cmd = "bugzilla attach --getall 663674 --ignore-obsolete"
    fakebz = tests.mockbackend.make_bz(
        bug_attachment_get_all_args="data/mockargs/test_attach_get2.txt",
        bug_attachment_get_all_return="data/mockreturn/test_attach_get2.txt")
    out = run_cli(cmd, fakebz)

    os.system("ls %s" % os.getcwd())
    filename += ".1"
    assert filename in out
    assert "bugzilla-filename" in out


def test_attach_get(run_cli):
    import tempfile
    import shutil
    tmpdir = tempfile.mkdtemp(dir=os.getcwd())
    origcwd = os.getcwd()
    os.chdir(tmpdir)
    try:
        _test_attach_get(run_cli)
    finally:
        os.chdir(origcwd)
        shutil.rmtree(tmpdir)
