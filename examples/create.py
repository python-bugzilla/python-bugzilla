#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# create.py: Create a new bug report

from __future__ import print_function

import time

import bugzilla

# public test instance of bugzilla.redhat.com.
#
# Don't worry, changing things here is fine, and won't send any email to
# users or anything. It's what partner-bugzilla.redhat.com is for!
URL = "partner-bugzilla.redhat.com"
bzapi = bugzilla.Bugzilla(URL)
if not bzapi.logged_in:
    print("This example requires cached login credentials for %s" % URL)
    bzapi.interactive_login()


# Similar to build_query, build_createbug is a helper function that handles
# some bugzilla version incompatibility issues. All it does is return a
# properly formatted dict(), and provide friendly parameter names.
# The argument names map to those accepted by XMLRPC Bug.create:
# https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#create-bug
#
# The arguments specified here are mandatory, but there are many other
# optional ones like op_sys, platform, etc. See the docs
createinfo = bzapi.build_createbug(
    product="Fedora",
    version="rawhide",
    component="python-bugzilla",
    summary="new example python-bugzilla bug %s" % time.time(),
    description="This is comment #0 of an example bug created by "
                "the python-bugzilla.git examples/create.py script.")

newbug = bzapi.createbug(createinfo)
print("Created new bug id=%s url=%s" % (newbug.id, newbug.weburl))
