#
# Copyright Red Hat, Inc. 2012
#
# This work is licensed under the terms of the GNU GPL, version 2 or later.
# See the COPYING file in the top-level directory.
#

'''
Unit tests for building query strings with bin/bugzilla
'''

import copy
import os
import unittest

import tests

bz34 = tests.make_bz("3.4.0")
bz4 = tests.make_bz("4.0.0")
rhbz4 = tests.make_bz("4.4.0", rhbz=True)


class BZ34Test(unittest.TestCase):
    """
    This is the base query class, but it's also functional on its
    own.
    """
    maxDiff = None

    def assertDictEqual(self, *args, **kwargs):
        # EPEL5 back compat
        if hasattr(unittest.TestCase, "assertDictEqual"):
            return unittest.TestCase.assertDictEqual(self, *args, **kwargs)
        return self.assertEqual(*args, **kwargs)

    def clicomm(self, argstr, out):
        comm = "bugzilla query --test-return-result " + argstr

        if out is None:
            self.assertRaises(RuntimeError, tests.clicomm, comm, self.bz)
        else:
            q = tests.clicomm(comm, self.bz, returnmain=True)
            self.assertDictEqual(out, q)

    def testBasicQuery(self):
        self.clicomm("--product foo --component foo,bar --bug_id 1234,2480",
                     self._basic_query_out)

    def testOneline(self):
        self.clicomm("--product foo --oneline", self._oneline_out)

    def testOutputFormat(self):
        self.clicomm("--product foo --outputformat "
                     "%{bug_id}:%{blockedby}:%{bug_status}:%{short_desc}:"
                     "%{status_whiteboard}:%{product}:%{rep_platform}",
                     self._output_format_out)

    def testBugStatusALL(self):
        self.clicomm("--product foo --bug_status ALL", self._status_all_out)

    def testBugStatusDEV(self):
        self.clicomm("--bug_status DEV", self._status_dev_out)

    def testBugStatusQE(self):
        self.clicomm("--bug_status QE", self._status_qe_out)

    def testBugStatusEOL(self):
        self.clicomm("--bug_status EOL", self._status_eol_out)

    def testBugStatusOPEN(self):
        self.clicomm("--bug_status OPEN", self._status_open_out)

    def testBugStatusRegular(self):
        self.clicomm("--bug_status POST", self._status_post_out)

    def testEmailOptions(self):
        cmd = ("--cc foo1@example.com "
               "--assigned_to foo2@example.com "
               "--reporter foo3@example.com "
               "--qa_contact foo7@example.com")
        self.clicomm(cmd, self._email_out)
        self.clicomm(cmd + " --emailtype notsubstring", self._email_type_out)

    def testComponentsFile(self):
        self.clicomm("--components_file " +
                    os.getcwd() + "/tests/data/components_file.txt",
                    self._components_file_out)

    def testKeywords(self):
        self.clicomm("--keywords Triaged "
                    "--url http://example.com --url_type foo",
                    self._keywords_out)

    def testBooleanChart(self):
        self.clicomm("--boolean_query 'keywords-substring-Partner & "
                    "keywords-notsubstring-OtherQA' "
                    "--boolean_query 'foo-bar-baz | foo-bar-wee' "
                    "--boolean_query '! foo-bar-yargh'", None)

    def testLongDesc(self):
        self.clicomm("--long_desc 'foobar'", self._longdesc_out)

    def testQuicksearch(self):
        self.clicomm("--quicksearch 'foo bar baz'", self._quicksearch_out)

    def testSavedsearch(self):
        self.clicomm("--savedsearch 'my saved search' "
            "--savedsearch-sharer-id 123456", self._savedsearch_out)

    def testSubComponent(self):
        self.clicomm("--component lvm2,kernel "
            "--sub-component 'Command-line tools (RHEL5)'",
            self._sub_component_out)

    # Test data. This is what subclasses need to fill in
    bz = bz34

    _basic_query_out = {'product': ['foo'], 'component': ['foo', 'bar'],
        'id': ["1234", "2480"]}
    _oneline_out = {'product': ['foo']}
    _output_format_out = {'product': ['foo']}
    output_format_out = _output_format_out

    _status_all_out = {'product': ['foo']}
    _status_dev_out = {'bug_status': ['NEW', 'ASSIGNED', 'NEEDINFO',
        'ON_DEV', 'MODIFIED', 'POST', 'REOPENED']}
    _status_qe_out = {'bug_status': ['ASSIGNED', 'ON_QA',
        'FAILS_QA', 'PASSES_QA']}
    _status_eol_out = {'bug_status': ['VERIFIED', 'RELEASE_PENDING',
        'CLOSED']}
    _status_open_out = {'bug_status': ['NEW', 'ASSIGNED', 'MODIFIED',
        'ON_DEV', 'ON_QA', 'VERIFIED', 'RELEASE_PENDING', 'POST']}
    _status_post_out = {'bug_status': ['POST']}
    _email_out = {'assigned_to': 'foo2@example.com',
        'cc': ["foo1@example.com"],
        'reporter': "foo3@example.com", "qa_contact": "foo7@example.com"}
    _email_type_out = {
        'email1': ['foo1@example.com'], 'email2': "foo2@example.com",
        'email3': 'foo3@example.com', 'email4': 'foo7@example.com',
        'emailtype1': 'notsubstring', 'emailtype2': 'notsubstring',
        'emailtype3': 'notsubstring', 'emailtype4': 'notsubstring',
        'emailcc1': True, 'emailassigned_to2': True,
        'emailreporter3': True, 'emailqa_contact4': True,
        'query_format': 'advanced'}
    _components_file_out = {'component': ["foo", "bar", "baz"]}
    _keywords_out = {'query_format': 'advanced',
        'field0-0-0': 'keywords', 'value0-0-0': 'Triaged',
        'field1-0-0': 'bug_file_loc', 'value1-0-0': 'http://example.com',
        'type0-0-0': 'substring', 'type1-0-0': 'foo'}
    _longdesc_out = {'longdesc': 'foobar', 'longdesc_type': 'allwordssubstr',
        'query_format': 'advanced'}
    _quicksearch_out = {'quicksearch': 'foo bar baz'}
    _savedsearch_out = {'savedsearch': "my saved search",
        'sharer_id': "123456"}
    _sub_component_out = {'component': ["lvm2", "kernel"],
        'sub_components': ["Command-line tools (RHEL5)"]}


class BZ4Test(BZ34Test):
    bz = bz4

    _default_includes = ['assigned_to', 'id', 'status', 'summary']

    _basic_query_out = BZ34Test._basic_query_out.copy()
    _basic_query_out["include_fields"] = _default_includes

    _oneline_out = BZ34Test._oneline_out.copy()
    _oneline_out["include_fields"] = ['assigned_to', 'blocks', 'component',
        'flags', 'keywords', 'status', 'target_milestone', 'id']

    _output_format_out = BZ34Test._output_format_out.copy()
    _output_format_out["include_fields"] = ['product', 'summary',
        'platform', 'status', 'id', 'blocks', 'whiteboard']

    _status_all_out = BZ34Test._status_all_out.copy()
    _status_all_out["include_fields"] = _default_includes

    _status_dev_out = BZ34Test._status_dev_out.copy()
    _status_dev_out["include_fields"] = _default_includes

    _status_qe_out = BZ34Test._status_qe_out.copy()
    _status_qe_out["include_fields"] = _default_includes

    _status_eol_out = BZ34Test._status_eol_out.copy()
    _status_eol_out["include_fields"] = _default_includes

    _status_open_out = BZ34Test._status_open_out.copy()
    _status_open_out["include_fields"] = _default_includes

    _status_post_out = BZ34Test._status_post_out.copy()
    _status_post_out["include_fields"] = _default_includes

    _email_out = BZ34Test._email_out.copy()
    _email_out["include_fields"] = _default_includes

    _email_type_out = BZ34Test._email_type_out.copy()
    _email_type_out["include_fields"] = _default_includes

    _components_file_out = BZ34Test._components_file_out.copy()
    _components_file_out["include_fields"] = _default_includes

    _keywords_out = BZ34Test._keywords_out.copy()
    _keywords_out["include_fields"] = _default_includes

    _longdesc_out = BZ34Test._longdesc_out.copy()
    _longdesc_out["include_fields"] = _default_includes

    _quicksearch_out = BZ34Test._quicksearch_out.copy()
    _quicksearch_out["include_fields"] = _default_includes
    _savedsearch_out = BZ34Test._savedsearch_out.copy()
    _savedsearch_out["include_fields"] = _default_includes
    _sub_component_out = BZ34Test._sub_component_out.copy()
    _sub_component_out["include_fields"] = _default_includes


class RHBZTest(BZ4Test):
    bz = rhbz4

    _output_format_out = BZ34Test.output_format_out.copy()
    _output_format_out["include_fields"] = ['product', 'summary',
        'platform', 'status', 'id', 'blocks', 'whiteboard']
    _booleans_out = {}

    def testTranslation(self):
        def translate(_in):
            _out = copy.deepcopy(_in)
            self.bz.pre_translation(_out)
            return _out

        in_query = {
            "fixed_in": "foo.bar",
            "product": "some-product",
            "cf_devel_whiteboard": "some_devel_whiteboard",
            "include_fields": ["fixed_in",
                "components", "cf_devel_whiteboard"],
        }
        out_query = translate(in_query)

        in_query["include_fields"] = [
            "cf_devel_whiteboard", "cf_fixed_in", "component", "id"]
        self.assertDictEqual(in_query, out_query)

        in_query = {"bug_id": "123,456", "component": "foo,bar"}
        out_query = translate(in_query)
        self.assertEqual(out_query["id"], ["123", "456"])
        self.assertEqual(out_query["component"], ["foo", "bar"])

        in_query = {"bug_id": [123, 124], "column_list": ["id"]}
        out_query = translate(in_query)
        self.assertEqual(out_query["id"], [123, 124])
        self.assertEqual(out_query["include_fields"], in_query["column_list"])

    def testInvalidBoolean(self):
        self.assertRaises(RuntimeError, self.bz.build_query,
            boolean_query="foobar")

    def testBooleans(self):
        out = {
            'query_format': 'advanced',
            'type0-0-0': 'substring',
            'type1-0-0': 'substring',
            'type2-0-0': 'substring',
            'type3-0-0': 'substring',
            'value0-0-0': '123456',
            'value1-0-0': 'needinfo & devel_ack',
            'value2-0-0': '! baz foo',
            'value3-0-0': 'foobar | baz',
            'field0-0-0': 'blocked',
            'field1-0-0': 'flagtypes.name',
            'field2-0-0': 'cf_qa_whiteboard',
            'field3-0-0': 'cf_devel_whiteboard',
            'include_fields': ['assigned_to', 'id', 'status', 'summary'],
        }

        import bugzilla
        import logging
        log = logging.getLogger(bugzilla.__name__)
        handlers = log.handlers
        try:
            log.handlers = []
            self.clicomm("--blocked 123456 "
                        "--devel_whiteboard 'foobar | baz' "
                        "--qa_whiteboard '! baz foo' "
                        "--flag 'needinfo & devel_ack'", out)
        finally:
            log.handlers = handlers


class TestURLToQuery(BZ34Test):
    def _check(self, url, query):
        self.assertDictEqual(bz4.url_to_query(url), query)

    def testSavedSearch(self):
        url = ("https://bugzilla.redhat.com/buglist.cgi?"
            "cmdtype=dorem&list_id=2342312&namedcmd="
            "RHEL7%20new%20assigned%20virt-maint&remaction=run&"
            "sharer_id=321167")
        query = {
            'sharer_id': '321167',
            'savedsearch': 'RHEL7 new assigned virt-maint'
        }
        self._check(url, query)

    def testStandardQuery(self):
        url = ("https://bugzilla.redhat.com/buglist.cgi?"
            "component=virt-manager&query_format=advanced&classification="
            "Fedora&product=Fedora&bug_status=NEW&bug_status=ASSIGNED&"
            "bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&"
            "bug_status=VERIFIED&bug_status=FAILS_QA&bug_status="
            "RELEASE_PENDING&bug_status=POST&order=bug_status%2Cbug_id")
        query = {
            'product': 'Fedora',
            'query_format': 'advanced',
            'bug_status': ['NEW', 'ASSIGNED', 'MODIFIED', 'ON_DEV',
                'ON_QA', 'VERIFIED', 'FAILS_QA', 'RELEASE_PENDING', 'POST'],
            'classification': 'Fedora',
            'component': 'virt-manager',
            'order': 'bug_status,bug_id'
        }
        self._check(url, query)
