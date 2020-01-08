
from __future__ import print_function

import os
import shlex
import sys

# pylint: disable=import-error
if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO
# pylint: enable=import-error

from bugzilla import Bugzilla, RHBugzilla, _cli


class _CLICONFIG(object):
    def __init__(self):
        self.REDHAT_URL = None
        self.REGENERATE_OUTPUT = False


CLICONFIG = _CLICONFIG()
os.environ["__BUGZILLA_UNITTEST"] = "1"


def clicomm(argvstr, bzinstance,
        returnmain=False, stdin=None, expectfail=False):
    """
    Run bin/bugzilla.main() directly with passed argv
    """

    argv = shlex.split(argvstr)

    oldstdout = sys.stdout
    oldstderr = sys.stderr
    oldstdin = sys.stdin
    oldargv = sys.argv
    try:
        out_io = StringIO()
        sys.stdout = out_io
        sys.stderr = out_io
        if stdin:
            sys.stdin = stdin

        sys.argv = argv

        ret = 0
        test_return = None
        try:
            print(" ".join(argv))
            print()

            test_return = _cli.main(unittest_bz_instance=bzinstance)
        except SystemExit as sys_e:
            ret = sys_e.code

        outstr = out_io.getvalue()
        if outstr.endswith("\n"):
            outstr = outstr[:-1]

        if ret != 0 and not expectfail:
            raise RuntimeError("Command failed with %d\ncmd=%s\nout=%s" %
                               (ret, argvstr, outstr))
        if ret == 0 and expectfail:
            raise RuntimeError("Command succeeded but we expected success\n"
                               "ret=%d\ncmd=%s\nout=%s" %
                               (ret, argvstr, outstr))

        if returnmain:
            return test_return
        return outstr
    finally:
        sys.stdout = oldstdout
        sys.stderr = oldstderr
        sys.stdin = oldstdin
        sys.argv = oldargv
