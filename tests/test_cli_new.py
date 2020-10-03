# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import tests
import tests.mockbackend
import tests.utils


###############################
# 'bugzilla new' mock testing #
###############################

def test_new(run_cli):
    # Test a simpler creation
    cmd = "bugzilla new --product FOOPROD --component FOOCOMP "
    cmd += "--summary 'Hey this is the title!' "
    cmd += "--comment 'This is the first comment!\nWith newline & stuff.' "
    cmd += "--keywords ADDKEY --groups FOOGROUP,BARGROUP "
    cmd += "--blocked 12345,6789 --cc foo@example.com --cc bar@example.com "
    cmd += "--dependson dependme --private "

    fakebz = tests.mockbackend.make_bz(
        bug_create_args="data/mockargs/test_new1.txt",
        bug_create_return={"id": 1694158},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug.txt")
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_new1.txt")

    # Test every option
    cmd = "bugzilla new --product FOOPROD --component FOOCOMP "
    cmd += "--summary 'Hey this is the title!' "
    cmd += "--comment 'This is the first comment!\nWith newline & stuff.' "
    cmd += "--keywords ADDKEY --groups FOOGROUP,BARGROUP "
    cmd += "--blocked 12345,6789 --cc foo@example.com --cc bar@example.com "
    cmd += "--dependson dependme --private "
    cmd += "--os linux --arch mips --severity high --priority low "
    cmd += "--url https://some.example.com "
    cmd += "--version 5.6.7 --alias somealias "
    cmd += "--sub-component FOOCOMP "
    cmd += "--assignee foo@example.com --qa_contact qa@example.com "
    cmd += "--comment-tag FOO "
    cmd += "--field foo=bar "

    fakebz = tests.mockbackend.make_bz(
        bug_create_args="data/mockargs/test_new2.txt",
        bug_create_return={"id": 1694158},
        bug_get_args=None,
        bug_get_return="data/mockreturn/test_getbug.txt",
        rhbz=True)
    out = run_cli(cmd, fakebz)
    tests.utils.diff_compare(out, "data/clioutput/test_new2.txt")
