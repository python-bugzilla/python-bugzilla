# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import tests
import tests.mockbackend
import tests.utils


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
    prod_get_comp_active = {'products': [
        {'id': 7, 'name': 'test-fake-product',
         'components': [
             {'is_active': True, 'name': 'backend/kernel'},
             {'is_active': True, 'name': 'client-interfaces'},
         ]},
    ]}
    cmd = "bugzilla info --components test-fake-product"
    fakebz = tests.mockbackend.make_bz(
        product_get_args=argsprefix + "components.txt",
        product_get_return=prod_get_comp_active)
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, cliprefix + "components.txt")

    # info --components --active-components
    cmd = "bugzilla info --components test-fake-product --active-components"
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
