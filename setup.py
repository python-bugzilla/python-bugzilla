#!/usr/bin/env python3

from __future__ import print_function

import glob
import os
import sys

from distutils.core import Command
from setuptools import setup


def unsupported_python_version():
    return sys.version_info < (2, 7) \
        or (sys.version_info > (3,) and sys.version_info < (3, 4))


if unsupported_python_version():
    raise ImportError("python-bugzilla does not support this python version")


def get_version():
    f = open("bugzilla/apiversion.py")
    for line in f:
        if line.startswith('version = '):
            return eval(line.split('=')[-1])  # pylint: disable=eval-used


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        print("\n* Tests are now run with the 'pytest' tool.\n"
              "* See CONTRIBUTING.md for details.")


class PylintCommand(Command):
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        import pylint.lint
        import pycodestyle

        files = (["bugzilla-cli", "bugzilla", "setup.py"] +
            glob.glob("examples/*.py") +
            glob.glob("tests/*.py"))
        output_format = sys.stdout.isatty() and "colorized" or "text"

        print("running pycodestyle")
        style_guide = pycodestyle.StyleGuide(
            config_file='tox.ini',
            format="pylint",
            paths=files,
        )
        report = style_guide.check_files()
        if style_guide.options.count:
            sys.stderr.write(str(report.total_errors) + '\n')

        print("running pylint")
        pylint_opts = [
            "--rcfile", "pylintrc",
            "--output-format=%s" % output_format,
        ]
        pylint.lint.Run(files + pylint_opts)


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


setup(
    name='python-bugzilla',
    version=get_version(),
    description='Bugzilla XMLRPC access module',
    author='Cole Robinson',
    author_email='python-bugzilla@lists.fedorahosted.org',
    license="GPLv2",
    url='https://github.com/python-bugzilla/python-bugzilla',
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['bugzilla'],
    entry_points={'console_scripts': ['bugzilla = bugzilla._cli:cli']},
    data_files=[('share/man/man1', ['bugzilla.1'])],

    install_requires=_parse_requirements("requirements.txt"),
    tests_require=_parse_requirements("test-requirements.txt"),

    cmdclass={
        "pylint": PylintCommand,
        "rpm": RPMCommand,
        "test": TestCommand,
    },
)
