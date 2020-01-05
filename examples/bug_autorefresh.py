#!/usr/bin/env python
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

# bug_autorefresh.py: Show what bug_autorefresh is all about, and explain
#   how to handle the default change via python-bugzilla in 2016

from __future__ import print_function

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
URL = "partner-bugzilla.redhat.com"
bzapi = bugzilla.Bugzilla(URL)

# The Bugzilla.bug_autorefresh setting controls whether bugs will
# automatically go out and try to update their cached contents when code
# tries to access a bug attribute that isn't already cached.
#
# Note this is likely only relevant if some part of your code is using
# include_fields, or exclude_fields, or you are depending on access
# to bugzilla.redhat.com 'extra_fields' type data like 'attachments'
# without explicitly asking the API for them. If you aren't using any
# of those bits, you can ignore this.
#
# Though if you aren't using include_fields and you are running regular
# queries in a script, check examples/query.py for a simple usecase that
# shows how much include_fields usage can speed up your scripts.

# The default as of mid 2016 is bug_autorefresh=off, so set it True here
# to demonstrate
bzapi.bug_autorefresh = True
bug = bzapi.getbug(427301, include_fields=["id", "summary"])

# The limited include_fields here means that only "id" and "summary" fields
# of the bug are cached in the bug object. What happens when we try to
# get component for example?
print("Bug component=%s" % bug.component)

# Because bug_autorefresh is True, the bug object basically did a
# a bug.refresh() for us, grabbed all its data, and now the component field
# is there. Let's try it again, but this time without bug_autorefresh
bzapi.bug_autorefresh = False
bug = bzapi.getbug(427301, include_fields=["id", "summary"])
try:
    print("Shouldn't see this! bug component=%s" % bug.component)
except AttributeError:
    print("With bug_autorefresh=False, we received AttributeError as expected")

# Why does this matter? Some scripts are implicitly depending on this
# auto-refresh behavior, because their include_fields specification doesn't
# cover all attributes they actually use. Your script will work, sure, but
# it's likely doing many more XML-RPC calls than needed, possibly 1 per bug.
# So if after upgrading python-bugzilla you start hitting issues, the
# recommendation is to fix your include_fields.
