#!/usr/bin/python
# Simple self-test of the bugzilla module

# Copyright (C) 2007 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from bugzilla import Bugzilla
import os, glob, sys

def find_firefox_cookiefile():
    cookieglob = os.path.expanduser('~/.mozilla/firefox/default.*/cookies.txt')
    cookiefiles = glob.glob(cookieglob)
    if cookiefiles:
        # TODO return whichever is newest
        return cookiefiles[0]

def selftest():
    url = 'https://bugzilla.redhat.com/xmlrpc.cgi'
    cookies = find_firefox_cookiefile()
    public_bug = 1
    private_bug = 250666
    print "Woo, welcome to the bugzilla.py self-test."
    print "Using bugzilla at " + url
    if not cookies:
        print "Could not find any cookies for that URL!"
        print "Log in with firefox or give me a username/password."
        sys.exit(1)
    print "Reading cookies from " + cookies
    b = Bugzilla(url=url,cookies=cookies)
    print "Reading product list"
    print b.products()
    print "Reading public bug (#%i)" % public_bug
    print b.getbugsimple(public_bug)
    print "Reading private bug (#%i)" % private_bug
    try:
        print b.getbugsimple(private_bug)
    except xmlrpclib.Fault, e:
        if 'NotPermitted' in e.faultString:
            print "Failed: Not authorized."
        else:
            print "Failed: Unknown XMLRPC error: %s"  % e
    print "Awesome. We're done."

if __name__ == '__main__':
    selftest()
