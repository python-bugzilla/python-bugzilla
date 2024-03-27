# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import difflib
import getpass
import inspect
import io
import os
import pprint
import shlex
import sys

from bugzilla import Bugzilla
import bugzilla._cli

import tests


def get_funcname():
    # Return calling function name
    return inspect.stack()[1][3]


def tests_path(filename):
    testdir = os.path.dirname(__file__)
    if testdir not in filename:
        return os.path.join(testdir, filename)
    return filename


def monkeypatch_getpass(monkeypatch):
    monkeypatch.setattr(getpass, "getpass", input)


def sanitize_json(rawout):
    # py2.7 leaves trailing whitespace after commas. strip it so
    # tests pass on both python versions
    return "\n".join([line.rstrip() for line in rawout.splitlines()])


def open_functional_bz(bzclass, url, kwargs):
    bz = bzclass(url, **kwargs)

    if kwargs.get("force_rest", False):
        assert bz.is_rest() is True
    if kwargs.get("force_xmlrpc", False):
        assert bz.is_xmlrpc() is True

    # Set a request timeout of 60 seconds
    os.environ["PYTHONBUGZILLA_REQUESTS_TIMEOUT"] = "60"
    return bz


def open_bz(url, bzclass=Bugzilla, **kwargs):
    return open_functional_bz(bzclass=bzclass, url=url, kwargs=kwargs)


def diff_compare(inputdata, filename, expect_out=None):
    """Compare passed string output to contents of filename"""
    def _process(data):
        if isinstance(data, tuple) and len(data) == 1:
            data = data[0]
        if isinstance(data, (dict, tuple)):
            out = pprint.pformat(data, width=81)
        else:
            out = str(data)
        if not out.endswith("\n"):
            out += "\n"
        return out

    actual_out = _process(inputdata)

    if filename:
        filename = tests_path(filename)
        if not os.path.exists(filename) or tests.CLICONFIG.REGENERATE_OUTPUT:
            open(filename, "w").write(actual_out)
        expect_out = open(filename).read()
    else:
        expect_out = _process(expect_out)

    diff = "".join(difflib.unified_diff(expect_out.splitlines(1),
                                        actual_out.splitlines(1),
                                        fromfile=filename or "Manual input",
                                        tofile="Generated Output"))
    if diff:
        raise AssertionError("Conversion outputs did not match.\n%s" % diff)


def do_run_cli(capsys, monkeypatch,
               argvstr, bzinstance,
               expectfail=False, stdin=None):
    """
    Run bin/bugzilla.main() directly with passed argv
    """
    argv = shlex.split(argvstr)
    monkeypatch.setattr(sys, "argv", argv)
    if stdin:
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    else:
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    ret = 0
    try:
        # pylint: disable=protected-access
        if bzinstance is None:
            bugzilla._cli.cli()
        else:
            bugzilla._cli.main(unittest_bz_instance=bzinstance)
    except SystemExit as sys_e:
        ret = sys_e.code

    out, err = capsys.readouterr()
    outstr = out + err

    if ret != 0 and not expectfail:
        raise RuntimeError("Command failed with %d\ncmd=%s\nout=%s" %
                           (ret, argvstr, outstr))
    if ret == 0 and expectfail:
        raise RuntimeError("Command succeeded but we expected success\n"
                           "ret=%d\ncmd=%s\nout=%s" %
                           (ret, argvstr, outstr))
    return outstr
