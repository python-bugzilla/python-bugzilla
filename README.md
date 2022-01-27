[![CI](https://github.com/python-bugzilla/python-bugzilla/workflows/CI/badge.svg)](https://github.com/python-bugzilla/python-bugzilla/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/python-bugzilla/python-bugzilla/branch/main/graph/badge.svg?token=4R3FR4RVH4)](https://codecov.io/gh/python-bugzilla/python-bugzilla)
[![PyPI](https://img.shields.io/pypi/v/python-bugzilla)](https://pypi.org/project/python-bugzilla/)

# python-bugzilla

This package provides two bits:

* `bugzilla` python module for talking to a [Bugzilla](https://www.bugzilla.org/) instance over XMLRPC or REST
* `/usr/bin/bugzilla` command line tool for performing actions from the command line: create or edit bugs, various queries, etc.

This was originally written specifically for [Red Hat's Bugzilla instance](https://bugzilla.redhat.com)
and is used heavily at Red Hat and in Fedora, but it should be
generically useful.

You can find some code examples in the [examples](examples) directory.

For questions about submitting patches, see [CONTRIBUTING.md](CONTRIBUTING.md)
