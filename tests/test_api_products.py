# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import pytest

import bugzilla

import tests
import tests.mockbackend


def test_api_component_edit():
    fakebz = tests.mockbackend.make_bz(
        component_create_args="data/mockargs/test_api_component_create1.txt",
        component_create_return={},
        component_update_args="data/mockargs/test_api_component_update1.txt",
        component_update_return={},
    )

    # addcomponent stub testing
    fakebz.addcomponent({
        "initialowner": "foo@example.com",
        "initialqacontact": "foo2@example.com",
        "initialcclist": "foo3@example.com",
        "product": "fooproduct",
        "is_active": 0,
    })

    # editcomponent stub testing
    fakebz.editcomponent({
        "initialowner": "foo@example.com",
        "blaharg": "blahval",
        "product": "fooproduct",
        "component": "foocomponent",
        "is_active": 0,
    })


def test_api_products():
    prod_list_return = {'ids': [1, 7]}
    prod_get_return = {'products': [
        {'id': 7, 'name': 'test-fake-product',
         'foo': {"bar": "baz"},
         'components': [
             {'default_assigned_to': 'Fake Guy',
              'name': 'client-interfaces'},
             {'default_assigned_to': 'ANother fake dude!',
              'name': 'configuration'},
         ]},
    ]}

    compnames = ["client-interfaces", "configuration"]
    fakebz = tests.mockbackend.make_bz(
        product_get_enterable_args=None,
        product_get_enterable_return=prod_list_return,
        product_get_selectable_args=None,
        product_get_selectable_return=prod_list_return,
        product_get_args="data/mockargs/test_api_products_get1.txt",
        product_get_return=prod_get_return,
    )

    # enterable products
    fakebz.product_get(ptype="enterable")
    fakebz.product_get(ptype="selectable")
    with pytest.raises(RuntimeError):
        fakebz.product_get(ptype="idontknow")

    # Double refresh things
    fakebz.getproducts(force_refresh=True, ptype="enterable")
    fakebz.getproducts(force_refresh=True, ptype="enterable")

    # getcomponents etc. testing
    fakebz = tests.mockbackend.make_bz(
        product_get_args="data/mockargs/test_api_products_get2.txt",
        product_get_return=prod_get_return,
    )

    # Lookup in product cache by name
    ret = fakebz.getcomponents("test-fake-product")
    assert ret == compnames
    # Lookup in product cache by id
    ret = fakebz.getcomponents(7)
    assert ret == compnames
    # force_refresh but its cool
    ret = fakebz.getcomponents("test-fake-product", force_refresh=True)
    assert ret == compnames

    # getcomponentsdetails usage
    fakebz = tests.mockbackend.make_bz(
        product_get_args="data/mockargs/test_api_products_get3.txt",
        product_get_return=prod_get_return,
    )
    fakebz.getcomponentdetails("test-fake-product", "configuration")

    # Some bit to test productget exclude_args
    fakebz = tests.mockbackend.make_bz(
        product_get_args="data/mockargs/test_api_products_get4.txt",
        product_get_return=prod_get_return)
    fakebz.product_get(ids=["7"], exclude_fields=["product.foo"])

    # Unknown product
    fakebz = tests.mockbackend.make_bz(
        product_get_args="data/mockargs/test_api_products_get5.txt",
        product_get_return=prod_get_return)
    with pytest.raises(bugzilla.BugzillaError):
        fakebz.getcomponents(0)



def test_bug_fields():
    fakebz = tests.mockbackend.make_bz(
        bug_fields_args="data/mockargs/test_bug_fields.txt",
        bug_fields_return="data/mockreturn/test_bug_fields.txt",
    )
    ret = fakebz.getbugfields(names=["bug_status"])
    assert ["bug_status"] == ret
