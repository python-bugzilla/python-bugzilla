#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# create.py: Create a new bug report

from __future__ import print_function

import bugzilla

# Don't worry, changing things here is fine, and won't send any email to
# users or anything. It's what landfill.bugzilla.org is for!
URL = "https://landfill.bugzilla.org/bugzilla-5.0-branch/xmlrpc.cgi"

print("You can get an API key at "
      "https://landfill.bugzilla.org/bugzilla-5.0-branch/userprefs.cgi")
print("after creating an account, if necessary.  "
      "This is a test site, so no harm will come!")
api_key = raw_input("Enter Bugzilla API Key: ")

# API key usage assumes the API caller is storing the API key; if you would
# like to use one of the login options that stores credentials on-disk for
# command-line usage, use tokens or cookies.
bzapi = bugzilla.Bugzilla(URL, api_key=api_key)
assert bzapi.logged_in
