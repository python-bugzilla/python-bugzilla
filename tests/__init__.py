
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


# This is overwritten by python setup.py test --redhat-url, and then
# used in ro/rw tests
REDHAT_URL = None


def make_bz(version, *args, **kwargs):
    cls = Bugzilla
    if kwargs.pop("rhbz", False):
        cls = RHBugzilla
    if "cookiefile" not in kwargs and "tokenfile" not in kwargs:
        kwargs["use_creds"] = False
    if "url" not in kwargs:
        kwargs["url"] = None
    bz = cls(*args, **kwargs)
    bz._set_bz_version(version)  # pylint: disable=protected-access
    return bz


def clicomm(argv, bzinstance, returnmain=False, stdin=None, expectfail=False):
    """
    Run bin/bugzilla.main() directly with passed argv
    """

    argv = shlex.split(argv)

    oldstdout = sys.stdout
    oldstderr = sys.stderr
    oldstdin = sys.stdin
    oldargv = sys.argv
    try:
        out = StringIO()
        sys.stdout = out
        sys.stderr = out
        if stdin:
            sys.stdin = stdin

        sys.argv = argv

        ret = 0
        mainout = None
        try:
            print(" ".join(argv))
            print()

            mainout = _cli.main(unittest_bz_instance=bzinstance)
        except SystemExit as sys_e:
            ret = sys_e.code

        outt = out.getvalue()
        if outt.endswith("\n"):
            outt = outt[:-1]

        if ret != 0 and not expectfail:
            raise RuntimeError("Command failed with %d\ncmd=%s\nout=%s" %
                               (ret, argv, outt))
        elif ret == 0 and expectfail:
            raise RuntimeError("Command succeeded but we expected success\n"
                               "ret=%d\ncmd=%s\nout=%s" % (ret, argv, outt))

        if returnmain:
            return mainout
        return outt
    finally:
        sys.stdout = oldstdout
        sys.stderr = oldstderr
        sys.stdin = oldstdin
        sys.argv = oldargv
