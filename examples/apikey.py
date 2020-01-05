#!/usr/bin/env python
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

# create.py: Create a new bug report

from __future__ import print_function
import sys

import bugzilla

# Don't worry, changing things here is fine, and won't send any email to
# users or anything. It's what landfill.bugzilla.org is for!
URL = "https://landfill.bugzilla.org/bugzilla-5.0-branch/xmlrpc.cgi"

print("You can get an API key at:\n "
      "    https://landfill.bugzilla.org/bugzilla-5.0-branch/userprefs.cgi")
print("This is a test site, so no harm will come!\n")

# pylint: disable=undefined-variable
if sys.version_info[0] >= 3:
    api_key = input("Enter Bugzilla API Key: ")
else:
    api_key = raw_input("Enter Bugzilla API Key: ")
# pylint: enable=undefined-variable

# API key usage assumes the API caller is storing the API key; if you would
# like to use one of the login options that stores credentials on-disk for
# command-line usage, use tokens or cookies.
bzapi = bugzilla.Bugzilla(URL, api_key=api_key)
assert bzapi.logged_in
