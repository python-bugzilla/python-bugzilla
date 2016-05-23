#
# Copyright Red Hat, Inc. 2013
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for building createbug dictionaries with bin/bugzilla
'''

import unittest

import tests


bz4 = tests.make_bz("4.0.0")


class CreatebugTest(unittest.TestCase):
    maxDiff = None
    bz = bz4

    def assertDictEqual(self, *args, **kwargs):
        # EPEL5 back compat
        if hasattr(unittest.TestCase, "assertDictEqual"):
            return unittest.TestCase.assertDictEqual(self, *args, **kwargs)
        return self.assertEqual(*args, **kwargs)

    def clicomm(self, argstr, out):
        comm = "bugzilla new --test-return-result " + argstr

        if out is None:
            self.assertRaises(RuntimeError, tests.clicomm, comm, self.bz)
        else:
            q = tests.clicomm(comm, self.bz, returnmain=True)
            self.assertDictEqual(out, q)

    def testBasic(self):
        self.clicomm(
            "--product foo --component bar --summary baz --version 12",
            {'component': 'bar', 'product': 'foo',
             'summary': 'baz', 'version': '12'}
        )

    def testOpSys(self):
        self.clicomm(
            "--os windowsNT --arch ia64 --comment 'youze a foo' --cc me",
            {'description': 'youze a foo', 'op_sys': 'windowsNT',
             'platform': 'ia64', 'cc': ["me"]}
        )

    def testSeverity(self):
        self.clicomm(
            "--severity HIGH --priority Low --url http://example.com",
            {'url': 'http://example.com', 'priority': 'Low',
             'severity': 'HIGH'}
        )

    def testMisc(self):
        self.clicomm(
            "--alias some-alias",
            {"alias": "some-alias"}
        )

    def testMultiOpts(self):
        # Test all opts that can take lists
        out = {'blocks': ['3', '4'], 'cc': ['1', '2'],
               'depends_on': ['5', 'foo', 'wib'], 'groups': ['bar', '8'],
               'keywords': ['TestOnly', 'ZStream']}
        self.clicomm(
            "--cc 1,2 --blocked 3,4 --dependson 5,foo,wib --groups bar,8 "
            "--keywords TestOnly,ZStream",
            out
        )
        self.clicomm(
            "--cc 1 --cc 2 --blocked 3 --blocked 4 "
            "--dependson 5,foo --dependson wib --groups bar --groups 8 "
            "--keywords TestOnly --keywords ZStream",
            out
        )

    def testFieldConversion(self):
        vc = self.bz._validate_createbug  # pylint: disable=protected-access
        out = vc(product="foo", component="bar",
            version="12", description="foo", short_desc="bar",
            check_args=False)
        self.assertDictEqual(out,
            {'component': 'bar', 'description': 'foo', 'product': 'foo',
             'summary': 'bar', 'version': '12'})
