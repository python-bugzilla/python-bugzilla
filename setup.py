#!/usr/bin/env python3

import glob
import os
import subprocess
import sys

import distutils.command.build
from distutils.core import Command
from setuptools import setup


def get_version():
    f = open("bugzilla/apiversion.py")
    for line in f:
        if line.startswith('version = '):
            return eval(line.split('=')[-1])  # pylint: disable=eval-used


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
            "--rcfile", ".pylintrc",
            "--output-format=%s" % output_format,
        ]
        pylint.lint.Run(files + pylint_opts)


class RPMCommand(Command):
    description = ("Build src and binary rpms and output them "
        "in the source directory")
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        self.run_command('sdist')
        srcdir = os.path.dirname(__file__)
        cmd = [
            "rpmbuild", "-ta",
            "--define", "_rpmdir %s" % srcdir,
            "--define", "_srcrpmdir %s" % srcdir,
            "--define", "_specdir /tmp",
            "dist/python-bugzilla-%s.tar.gz" % get_version(),
        ]
        subprocess.check_call(cmd)


class BuildCommand(distutils.command.build.build):
    def _make_man_pages(self):
        from distutils.spawn import find_executable
        rstbin = find_executable("rst2man")
        if not rstbin:
            rstbin = find_executable("rst2man.py")
        if not rstbin:
            sys.exit("Didn't find rst2man or rst2man.py")

        for path in glob.glob("man/*.rst"):
            base = os.path.basename(path)
            appname = os.path.splitext(base)[0]
            newpath = os.path.join(os.path.dirname(path),
                                   appname + ".1")

            print("Generating %s" % newpath)
            out = subprocess.check_output([rstbin, path])
            open(newpath, "wb").write(out)

            self.distribution.data_files.append(
                ('share/man/man1', (newpath,)))

    def run(self):
        self._make_man_pages()
        distutils.command.build.build.run(self)


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
    description='Library and command line tool for interacting with Bugzilla',
    license="GPLv2",
    url='https://github.com/python-bugzilla/python-bugzilla',
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=['bugzilla'],
    data_files=[],
    entry_points={'console_scripts': ['bugzilla = bugzilla._cli:cli']},

    install_requires=_parse_requirements("requirements.txt"),
    tests_require=_parse_requirements("test-requirements.txt"),

    cmdclass={
        "build": BuildCommand,
        "pylint": PylintCommand,
        "rpm": RPMCommand,
    },
)
