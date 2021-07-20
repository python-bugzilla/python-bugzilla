#!/usr/bin/env python
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

# getbug_restapi.py:
#            Simple demonstration of connecting to bugzilla over the REST
#            API and printing some bug details.

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
URL = "bugzilla.stage.redhat.com"

# By default, if plain Bugzilla(URL) is invoked, the Bugzilla class will
# attempt to determine if XMLRPC or REST API is available, with a preference
# for XMLRPC for back compatability. But you can use the REST API
# with force_rest=True
bzapi = bugzilla.Bugzilla(URL, force_rest=True)

# After that, the bugzilla API can be used as normal. See getbug.py for
# some more info here.
bug = bzapi.getbug(427301)
print("Fetched bug #%s:" % bug.id)
print("  Product   = %s" % bug.product)
print("  Component = %s" % bug.component)
print("  Status    = %s" % bug.status)
print("  Resolution= %s" % bug.resolution)
print("  Summary   = %s" % bug.summary)
