# Setting up the environment

If you already have system installed versions of python-bugzilla
dependencies, running the command line from git is as simple as doing:

    cd python-bugzilla.git
    ./bugzilla-cli [arguments]


# Running tests

Once you have already activated an environment, you can use the following.

## Basic unit test suite

    python setup.py test

## Read-Only Functional tests
There are more comprehensive tests that are disabled by default. Readonly
functional tests that run against several public bugzilla instances. No
login account is required:

    python setup.py test --ro-functional

## Read/Write Functional Tests.

Before running rw-functional tests, make sure you have logged into bugzilla
using. These currently run against the test bugzilla instance at
partner-bugzilla.redhat.com, and requires a valid login there:

    ./bugzilla-cli --bugzilla=partner-bugzilla.redhat.com --username=$USER login
    python setup.py test --rw-functional

## Testing across python versions
To test all supported python versions, run tox using any of the following.

    tox
    tox -- --ro-functional
    tox -- --rw-functional


# pylint and pycodestyle

To test for pylint or pycodestyle violations, you can run:

    python setup.py pylint

Note: This expects that you already have pylint and pycodestyle installed.


# Patch Submission

If you are submitting a patch, ensure the following:
    [REQ] verify that no new pylint or pycodestyle violations
    [REQ] run basic unit test suite across all python versions as described
        above.

Running any of the functional tests is not a requirement for patch submission,
but please give them a go if you are interested.

Patches can be submitted via github pull-request, or via the mailing list
at python-bugzilla@lists.fedorahosted.org using 'git send-email'.


# Bug reports

Bug reports should be submitted as github issues, or sent to the mailing list
