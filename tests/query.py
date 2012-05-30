import os
import unittest

from tests import clicomm

class QueryTest(unittest.TestCase):

    def testBasicQuery(self):
        q = clicomm("bugzilla --debug query --product foo --component bar")
        self.assertDictEqual(q, {'product': ['foo'], 'component': 'bar',
            'include_fields': ['bug_id', 'bug_status', 'assigned_to',
            'short_desc']})
