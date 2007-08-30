#!/usr/bin/python
# Simple self-test of the bugzilla module

from bugzilla import Bugzilla
import os, glob

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
    print "Reading cookies from " + cookies
    b = Bugzilla(url=url,cookies=cookies)
    print "Reading product list"
    print b.products()
    print "Reading public bug (#%i)" % public_bug
    print b.getbug(public_bug)
    print "Reading private bug (#%i)" % private_bug
    try:
        print b.getbug(private_bug)
    except xmlrpclib.Fault, e:
        if 'NotPermitted' in e.faultString:
            print "Failed: Not authorized."
        else:
            print "Failed: Unknown XMLRPC error: %s"  % e

if __name__ == '__main__':
    selftest()
