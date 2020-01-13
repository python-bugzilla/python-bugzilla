# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import json
import os
import re

import tests
import tests.mockbackend
import tests.utils


#################################
# 'bugzilla query' mock testing #
#################################

def test_query(run_cli):
    # bad field option
    fakebz = tests.mockbackend.make_bz()
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

    # RHBZ query with a ton of opts
    cmd = "bugzilla query "
    cmd += "--product foo --component foo,bar --bug_id 1234,2480 "
    cmd += "--keywords fribkeyword --fixed_in amifixed "
    cmd += "--qa_whiteboard some-example-whiteboard "
    cmd += "--cc foo@example.com --qa_contact qa@example.com "
    cmd += "--comment 'some comment string' "
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_search_args="data/mockargs/test_query1-rhbz.txt",
        bug_search_return="data/mockreturn/test_query1.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query1-rhbz.txt")

    # --emailtype handling
    cmd = "bugzilla query --cc foo@example.com --emailtype BAR "
    fakebz = tests.mockbackend.make_bz(rhbz=True,
        bug_search_args="data/mockargs/test_query2-rhbz.txt",
        bug_search_return="data/mockreturn/test_query1.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_query2-rhbz.txt")

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

    # Test --json output
    cmd = "bugzilla query --json --id 1165434"
    fakebz = tests.mockbackend.make_bz(
        bug_search_args="data/mockargs/test_query8.txt",
        bug_search_return={"bugs": [{"id": 1165434}]},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug_rhel.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(tests.utils.sanitize_json(out),
        "data/clioutput/test_query8.txt")
    assert json.loads(out)
