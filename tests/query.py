import os
import unittest

from bugzilla.bugzilla3 import Bugzilla34
from bugzilla.bugzilla4 import Bugzilla4
from bugzilla.rhbugzilla import RHBugzilla4

from tests import clicomm

bz34 = Bugzilla34(cookiefile=None)
bz4 = Bugzilla4(cookiefile=None)
rhbz4 = RHBugzilla4(cookiefile=None)

class BZ34Test(unittest.TestCase):
    """
    This is the base query class, but it's also functional on its
    own.
    """
    maxDiff = None

    def clicomm(self, argstr, out):
        comm = "bugzilla --debug query " + argstr
        q = clicomm(comm, self.bz)
        self.assertDictEqual(q, out)

    def testBasicQuery(self):
        self.clicomm("--product foo --component bar",
                     self._basic_query_out)
    def testOnline(self):
        self.clicomm("--product foo --oneline", self._online_out)

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
        self.clicomm("--cc foo@example.com "
                    "--assigned_to foo@example.com", self._email_out)

    def testComponentsFile(self):
        self.clicomm("--components_file " +
                    os.getcwd() + "/tests/data/components_file.txt",
                    self._components_file_out)

    def testKeywords(self):
        self.clicomm("--keywords Triaged "
                    "--url http://example.com --url_type foo",
                    self._keywords_out)

    def testBooleans(self):
        self.clicomm("--blocked 123456 "
                    "--devel_whiteboard 'foobar | baz' "
                    "--qa_whiteboard '! baz' "
                    "--flag 'needinfo & devel_ack'",
                    self._booleans_out)

    def testBooleanChart(self):
        self.clicomm("--boolean_query 'keywords-substring-Partner & "
                    "keywords-notsubstring-OtherQA' "
                    "--boolean_query 'foo-bar-baz | foo-bar-wee' "
                    "--boolean_query '! foo-bar-yargh'",
                    self._booleans_chart_out)


    # Test data. This is what subclasses need to fill in
    bz = bz34

    _basic_query_out = {'product': ['foo'], 'component': ['bar'],
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _online_out = {'product': ['foo'], 'include_fields': ['bug_id',
        'bug_status', 'assigned_to', 'component', 'target_milestone',
        'short_desc', 'flags', 'keywords', 'blockedby']}
    _status_all_out = {'product': ['foo'], 'include_fields':
        ['bug_id', 'bug_status', 'assigned_to', 'short_desc'],
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _status_dev_out = {'bug_status': ['NEW', 'ASSIGNED', 'NEEDINFO',
        'ON_DEV', 'MODIFIED', 'POST', 'REOPENED'], 'include_fields':
        ['bug_id', 'bug_status', 'assigned_to', 'short_desc'],
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _status_qe_out = {'bug_status': ['ASSIGNED', 'ON_QA',
        'FAILS_QA', 'PASSES_QA'], 'include_fields': ['bug_id',
        'bug_status', 'assigned_to', 'short_desc'], 'include_fields':
        ['bug_id', 'bug_status', 'assigned_to', 'short_desc']}
    _status_eol_out = {'bug_status': ['VERIFIED', 'RELEASE_PENDING',
        'CLOSED'], 'include_fields': ['bug_id', 'bug_status',
        'assigned_to', 'short_desc'], 'include_fields': ['bug_id',
        'bug_status', 'assigned_to', 'short_desc']}
    _status_open_out = {'bug_status': ['NEW', 'ASSIGNED', 'MODIFIED',
        'ON_DEV', 'ON_QA', 'VERIFIED', 'RELEASE_PENDING', 'POST'],
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _status_post_out = {'bug_status': ['POST'], 'include_fields':
        ['bug_id', 'bug_status', 'assigned_to', 'short_desc']}
    _email_out = {'assigned_to': 'foo@example.com', 'cc': "foo@example.com",
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _components_file_out = {'component': ["foo", "bar", "baz"],
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _keywords_out = {'keywords': 'Triaged', 'bug_file_loc':
        'http://example.com', 'bug_file_loc_type': 'foo',
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc']}
    _booleans_out = {'value2-0-0': 'baz', 'value0-0-0': '123456',
        'type3-0-1': 'substring', 'value1-1-0': 'devel_ack', 'type0-0-0':
        'substring', 'type2-0-0': 'substring', 'field3-0-1':
        'cf_devel_whiteboard', 'field3-0-0': 'cf_devel_whiteboard',
        'field1-0-0': 'flagtypes.name', 'value3-0-0': 'foobar',
        'value3-0-1': 'baz', 'value1-0-0': 'needinfo', 'type1-1-0':
        'substring', 'type1-0-0': 'substring', 'field1-1-0':
        'flagtypes.name', 'negate2': 1, 'field2-0-0':
        'cf_qa_whiteboard', 'type3-0-0': 'substring', 'field0-0-0':
        'blocked', 'include_fields': ['bug_id', 'bug_status',
        'assigned_to', 'short_desc'], 'query_format': 'advanced'}
    _booleans_chart_out = {'value1-0-1': 'wee', 'value2-0-0': 'yargh',
        'field2-0-0': 'foo', 'value0-0-0': 'Partner', 'type0-0-0':
        'substring', 'type2-0-0': 'bar', 'field1-0-1': 'foo', 'field1-0-0':
        'foo', 'value1-0-0': 'baz', 'field0-1-0': 'keywords', 'field0-0-0':
        'keywords', 'type1-0-0': 'bar', 'type1-0-1': 'bar', 'negate2': 1,
        'type0-1-0': 'notsubstring', 'value0-1-0': 'OtherQA',
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc'], 'query_format': 'advanced'}


class BZ4Test(BZ34Test):
    bz = bz4

class RHBZTest(BZ4Test):
    bz = rhbz4

    _email_out = {'email1': 'foo@example.com',
        'emailassigned_to2': True, 'emailtype2': 'substring', 'emailtype1':
        'substring', 'email2': 'foo@example.com', 'emailcc1': True,
        'include_fields': ['bug_id', 'bug_status', 'assigned_to',
        'short_desc'], 'query_format' : 'advanced'}
