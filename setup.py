import glob
import os
import sys
import unittest

from distutils.core import setup, Command

# XXX: importing this here means any external requirements are
# required at RPM build time. Should store canonical version in its
# own file
import bugzilla.base

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        testfiles = []
        for t in glob.glob(os.path.join(os.getcwd(), 'tests', '*.py')):
            if t.endswith("__init__.py"):
                continue
            base = os.path.basename(t)
            testfiles.append('.'.join(['tests', os.path.splitext(base)[0]]))

        try:
            # Use system 'coverage' if available
            import coverage
            use_coverage = True
        except:
            use_coverage = False

        tests = unittest.TestLoader().loadTestsFromNames(testfiles)
        t = unittest.TextTestRunner(verbosity=1)

        if use_coverage:
            coverage.erase()
            coverage.start()

        result = t.run(tests)

        if use_coverage:
            coverage.stop()

        err = int(bool(len(result.failures) > 0 or
                       len(result.errors) > 0))
        if not err and use_coverage:
            coverage.report(show_missing=False)
        sys.exit(err)


setup(name='python-bugzilla',
      version=str(bugzilla.base.version),
      description='Bugzilla XMLRPC access module',
      author='Will Woods',
      author_email='wwoods@redhat.com',
      url='https://fedorahosted.org/python-bugzilla/',
      packages = ['bugzilla'],
      scripts=['bin/bugzilla'],
      data_files=[('share/man/man1', ['bugzilla.1'])],

      cmdclass={
        "test" : TestCommand,
      }
)
