#!/usr/bin/env python

from __future__ import print_function

import glob
import os
import sys
import unittest

from distutils.core import Command
from setuptools import setup


def get_version():
    f = open("bugzilla/apiversion.py")
    for line in f:
        if line.startswith('version = '):
            return eval(line.split('=')[-1])


class TestCommand(Command):
    user_options = [
        ("ro-functional", None,
         "Run readonly functional tests against actual bugzilla instances. "
         "This will be very slow."),
        ("rw-functional", None,
         "Run read/write functional tests against actual bugzilla instances. "
         "As of now this only runs against partner-bugzilla.redhat.com, "
         "which requires an RH bugzilla account with cached cookies. "
         "This will also be very slow."),
        ("only=", None,
         "Run only tests whose name contains the passed string"),
        ("redhat-url=", None,
         "Redhat bugzilla URL to use for ro/rw_functional tests"),
        ("debug", None,
         "Enable python-bugzilla debug output. This may break output "
         "comparison tests."),
    ]

    def initialize_options(self):
        self.ro_functional = False
        self.rw_functional = False
        self.only = None
        self.redhat_url = None
        self.debug = False

    def finalize_options(self):
        pass

    def run(self):
        os.environ["__BUGZILLA_UNITTEST"] = "1"

        try:
            import coverage
            usecov = int(coverage.__version__.split(".")[0]) >= 3
        except:
            usecov = False

        if usecov:
            cov = coverage.coverage(omit=[
                "/*/tests/*", "/usr/*", "*dev-env*", "*.tox/*"])
            cov.erase()
            cov.start()

        testfiles = []
        for t in glob.glob(os.path.join(os.getcwd(), 'tests', '*.py')):
            if t.endswith("__init__.py"):
                continue

            base = os.path.basename(t)
            if (base == "ro_functional.py" and not self.ro_functional):
                continue

            if (base == "rw_functional.py" and not self.rw_functional):
                continue

            testfiles.append('.'.join(['tests', os.path.splitext(base)[0]]))


        if hasattr(unittest, "installHandler"):
            try:
                unittest.installHandler()
            except:
                print("installHandler hack failed")

        import tests as testsmodule
        testsmodule.REDHAT_URL = self.redhat_url
        if self.debug:
            import logging
            import bugzilla
            logging.getLogger(bugzilla.__name__).setLevel(logging.DEBUG)
            os.environ["__BUGZILLA_UNITTEST_DEBUG"] = "1"

        tests = unittest.TestLoader().loadTestsFromNames(testfiles)
        if self.only:
            newtests = []
            for suite1 in tests:
                for suite2 in suite1:
                    for testcase in suite2:
                        if self.only in str(testcase):
                            newtests.append(testcase)

            if not newtests:
                print("--only didn't find any tests")
                sys.exit(1)

            tests = unittest.TestSuite(newtests)
            print("Running only:")
            for test in newtests:
                print("%s" % test)
            print()


        t = unittest.TextTestRunner(verbosity=1)

        result = t.run(tests)

        if usecov:
            cov.stop()
            cov.save()

        err = int(bool(len(result.failures) > 0 or
                       len(result.errors) > 0))
        if not err and usecov:
            cov.report(show_missing=False)
        sys.exit(err)


class PylintCommand(Command):
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def _run(self):
        files = ["bugzilla/", "bin-bugzilla", "examples/*.py", "tests/*.py"]
        output_format = sys.stdout.isatty() and "colorized" or "text"

        cmd = "pylint "
        cmd += "--output-format=%s " % output_format
        cmd += " ".join(files)
        os.system(cmd + " --rcfile tests/pylint.cfg")

        print("running pep8")
        cmd = "pep8 "
        cmd += " ".join(files)
        os.system(cmd + " --config tests/pep8.cfg --exclude oldclasses.py")

    def run(self):
        os.link("bin/bugzilla", "bin-bugzilla")
        try:
            self._run()
        finally:
            try:
                os.unlink("bin-bugzilla")
            except:
                pass


class RPMCommand(Command):
    description = "Build src and binary rpms."
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        """
        Run sdist, then 'rpmbuild' the tar.gz
        """
        os.system("cp python-bugzilla.spec /tmp")
        try:
            os.system("rm -rf python-bugzilla-%s" % get_version())
            self.run_command('sdist')
            os.system('rpmbuild -ta --clean dist/python-bugzilla-%s.tar.gz' %
                      get_version())
        finally:
            os.system("mv /tmp/python-bugzilla.spec .")


def _parse_requirements(fname):
    ret = []
    for line in open(fname).readlines():
        if not line or line.startswith("#"):
            continue
        ret.append(line)
    return ret

setup(name='python-bugzilla',
      version=get_version(),
      description='Bugzilla XMLRPC access module',
      author='Cole Robinson',
      author_email='python-bugzilla@lists.fedorahosted.org',
      license="GPLv2",
      url='https://github.com/python-bugzilla/python-bugzilla',
      packages = ['bugzilla'],
      scripts=['bin/bugzilla'],
      data_files=[('share/man/man1', ['bugzilla.1'])],

      install_requires=_parse_requirements("requirements.txt"),
      tests_require=_parse_requirements("test-requirements.txt"),

      cmdclass={
        "pylint" : PylintCommand,
        "rpm" : RPMCommand,
        "test" : TestCommand,
      },
)
