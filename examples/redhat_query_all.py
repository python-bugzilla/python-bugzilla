#!/usr/bin/env python
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

# redhat_query_all.py: Perform a few varieties of queries

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
URL = "bugzilla.stage.redhat.com"

bzapi = bugzilla.Bugzilla(URL)


# In late 2021, bugzilla.redhat.com changed query() results to default to
# returning only 20 bugs. If the user passes in limit=0, that number changes
# to 1000, but is still capped if the query would return more than that.
#
# There's a discussion here with multiple proposed ways to work around it:
# https://github.com/python-bugzilla/python-bugzilla/issues/149
#
# This method uses ids_only=True, which is a custom bugzilla.redhat.com
# query feature to bypass the query limit by only returning matching bug IDs.
# rhbz feature bug: https://bugzilla.redhat.com/show_bug.cgi?id=2005153


# As of Feb 2024 this 1300+ bugs, which would have hit the query limit of 1000
query = bzapi.build_query(
    product="Fedora",
    component="virt-manager")
# Request the bugzilla.redhat.com extension ids_only=True to bypass limit
query["ids_only"] = True

queried_bugs = bzapi.query(query)
ids = [bug.id for bug in queried_bugs]
print(f"Queried {len(ids)} ids")


# Use getbugs to fetch the full list. getbugs is not affected by
# default RHBZ limits. However, requesting too much data via getbugs
# will timeout. This paginates the lookup to query 1000 bugs at a time.
#
# We also limit the returned data to just give us the `summary`.
# You should always limit your queries with include_fields` to only return
# the data you need.
count = 0
pagesize = 1000
include_fields = ["summary"]
while count < len(ids):
    idslice = ids[count:(count + pagesize)]
    print(f"Fetching data for bugs {count}-{count+len(idslice)-1}")
    bugs = bzapi.getbugs(idslice, include_fields=include_fields)
    print(f"Fetched {len(bugs)} bugs")
    count += pagesize
