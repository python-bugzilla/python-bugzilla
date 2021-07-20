# Setting up the environment

If you already have system installed versions of python-bugzilla
dependencies, running the command line from git is as simple as doing:

    cd python-bugzilla.git
    ./bugzilla-cli [arguments]


# Running tests

Our test suite uses pytest. If your system has dependencies already, the
quick unit test suite is invoked simply with:

    pytest

## Read-Only Functional tests

There are more comprehensive, readonly functional tests that run against
several public bugzilla instances, but they are not run by default. No
login account is required. Run them with:

     pytest --ro-functional

## Read/Write Functional Tests.

Read/Write functional tests use bugzilla.stage.redhat.com, which is a
bugzilla instance specifically for this type of testing. Data is occasionally
hard synced with regular bugzilla.redhat.com, and all local edits are
removed. Login accounts are also synced. If you want access to
bugzilla.stage.redhat.com, sign up for a regular bugzilla.redhat.com login
and wait for the next sync period.

Before running these tests, you'll need to cache login credentials.
Example:

    ./bugzilla-cli --bugzilla=bugzilla.stage.redhat.com --username=$USER login
    pytest --rw-functional

## Testing across python versions
To test all supported python versions, run tox using any of the following.

    tox
    tox -- --ro-functional
    tox -- --rw-functional


# pylint and pycodestyle

To test for pylint or pycodestyle violations, you can run:

    ./setup.py pylint

Note: This expects that you already have pylint and pycodestyle installed.


# Patch Submission

If you are submitting a patch, ensure the following:
    [REQ] verify that no new pylint or pycodestyle violations
    [REQ] run basic unit test suite across all python versions as described
        above.

Running any of the functional tests is not a requirement for patch submission,
but please give them a go if you are interested.
