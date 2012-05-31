import os
import unittest

from bugzilla.bugzilla3 import Bugzilla36

from tests import clicomm

bz34 = Bugzilla34(cookiefile=None)

class QueryTest(unittest.TestCase):
    maxDiff = None

    def clicomm(self, argstr):
        comm = "bugzilla --debug query " + argstr
        return clicomm(comm, bz34)

    def testBasicQuery(self):
        q = self.clicomm("--product foo --component bar")
        self.assertDictEqual(q, {'product': ['foo'], 'component': 'bar',
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc']})

    def testOnline(self):
        q = self.clicomm("--product foo --oneline")
        self.assertDictEqual(q, {'product': ['foo'], 'include_fields':
            ['bug_id', 'bug_status', 'assigned_to', 'component',
             'target_milestone', 'short_desc', 'flags', 'keywords',
             'blockedby']})

    def testBugStatusALL(self):
        q = self.clicomm("--product foo --bug_status ALL")
        self.assertDictEqual(q, {'product': ['foo'], 'include_fields':
            ['bug_id', 'bug_status', 'assigned_to', 'short_desc'],
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc']})
    def testBugStatusDEV(self):
        q = self.clicomm("--bug_status DEV")
        self.assertDictEqual(q, {'bug_status': ['NEW', 'ASSIGNED', 'NEEDINFO',
            'ON_DEV', 'MODIFIED', 'POST', 'REOPENED'], 'include_fields':
            ['bug_id', 'bug_status', 'assigned_to', 'short_desc'],
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc']})
    def testBugStatusQE(self):
        q = self.clicomm("--bug_status QE")
        self.assertDictEqual(q, {'bug_status': ['ASSIGNED', 'ON_QA',
            'FAILS_QA', 'PASSES_QA'], 'include_fields': ['bug_id',
            'bug_status', 'assigned_to', 'short_desc'], 'include_fields':
            ['bug_id', 'bug_status', 'assigned_to', 'short_desc']})
    def testBugStatusEOL(self):
        q = self.clicomm("--bug_status EOL")
        self.assertDictEqual(q, {'bug_status': ['VERIFIED', 'RELEASE_PENDING',
            'CLOSED'], 'include_fields': ['bug_id', 'bug_status',
            'assigned_to', 'short_desc'], 'include_fields': ['bug_id',
            'bug_status', 'assigned_to', 'short_desc']})
    def testBugStatusOPEN(self):
        q = self.clicomm("--bug_status OPEN")
        self.assertDictEqual(q, {'bug_status': ['NEW', 'ASSIGNED', 'MODIFIED',
            'ON_DEV', 'ON_QA', 'VERIFIED', 'RELEASE_PENDING', 'POST'],
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc']})
    def testBugStatusRegular(self):
        q = self.clicomm("--bug_status POST")
        self.assertDictEqual(q, {'bug_status': ['POST'], 'include_fields':
            ['bug_id', 'bug_status', 'assigned_to', 'short_desc']})

    def testEmailOptions(self):
        q = self.clicomm("--cc foo@example.com "
                    "--assigned_to foo@example.com")
        self.assertDictEqual(q, {'email1': 'foo@example.com',
            'emailassigned_to2': True, 'emailtype2': 'substring', 'emailtype1':
            'substring', 'email2': 'foo@example.com', 'emailcc1': True,
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc'], 'query_format' : 'advanced'})

    def testComponentsFile(self):
        q = self.clicomm("--components_file " +
                    os.getcwd() + "/tests/data/components_file.txt")
        self.assertDictEqual(q, {'component': 'foo,bar,baz', 'include_fields':
            ['bug_id', 'bug_status', 'assigned_to', 'short_desc']})

    def testKeywords(self):
        q = self.clicomm("--keywords Triaged "
                    "--url http://example.com --url_type foo")
        self.assertDictEqual(q, {'keywords': 'Triaged', 'bug_file_loc':
            'http://example.com', 'bug_file_loc_type': 'foo',
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc']})

    def testBooleans(self):
        q = self.clicomm("--blocked 123456 "
                    "--devel_whiteboard 'foobar | baz' "
                    "--qa_whiteboard '! baz' "
                    "--flag 'needinfo & devel_ack'")
        self.assertDictEqual(q, {'value2-0-0': 'baz', 'value0-0-0': '123456',
            'type3-0-1': 'substring', 'value1-1-0': 'devel_ack', 'type0-0-0':
            'substring', 'type2-0-0': 'substring', 'field3-0-1':
            'cf_devel_whiteboard', 'field3-0-0': 'cf_devel_whiteboard',
            'field1-0-0': 'flagtypes.name', 'value3-0-0': 'foobar',
            'value3-0-1': 'baz', 'value1-0-0': 'needinfo', 'type1-1-0':
            'substring', 'type1-0-0': 'substring', 'field1-1-0':
            'flagtypes.name', 'negate2': 1, 'field2-0-0':
            'cf_qa_whiteboard', 'type3-0-0': 'substring', 'field0-0-0':
            'blocked', 'include_fields': ['bug_id', 'bug_status',
            'assigned_to', 'short_desc'], 'query_format': 'advanced'})

    def testBooleanChart(self):
        q = self.clicomm("--boolean_query 'keywords-substring-Partner & "
                    "keywords-notsubstring-OtherQA' "
                    "--boolean_query 'foo-bar-baz | foo-bar-wee' "
                    "--boolean_query '! foo-bar-yargh'")
        self.assertDictEqual(q, {'value1-0-1': 'wee', 'value2-0-0': 'yargh',
            'field2-0-0': 'foo', 'value0-0-0': 'Partner', 'type0-0-0':
            'substring', 'type2-0-0': 'bar', 'field1-0-1': 'foo', 'field1-0-0':
            'foo', 'value1-0-0': 'baz', 'field0-1-0': 'keywords', 'field0-0-0':
            'keywords', 'type1-0-0': 'bar', 'type1-0-1': 'bar', 'negate2': 1,
            'type0-1-0': 'notsubstring', 'value0-1-0': 'OtherQA',
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc'], 'query_format': 'advanced'})
