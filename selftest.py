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
import xmlrpclib

bugzillas = {
        'Red Hat':{
            'url':'https://bugzilla.redhat.com/xmlrpc.cgi',
            'public_bug':1,
            'private_bug':250666,
            'bugidlist':(1,2,3,1337),
            'query':{'product':'Fedora',
                     'component':'kernel',
                     'version':'rawhide'}
            },
        'Bugzilla 3.0':{
            'url':'https://landfill.bugzilla.org/bugzilla-3.0-branch/xmlrpc.cgi',
            'public_bug':1,
            'private_bug':31337, # FIXME
            'bugidlist':(1,2,3,4433),
            'query':{'product':'WorldControl',
                     'component':'WeatherControl',
                     'version':'1.0'}
            },
        }
                     
# TODO: add data for these instances
# 'https://landfill.bugzilla.org/bugzilla-3.2-branch/xmlrpc.cgi' - BZ3.2
# 'https://partner-bugzilla.redhat.com/xmlrpc.cgi' - BZ3.2/RH hybrid

def selftest(data,user='',password=''):
    print "Using bugzilla at " + data['url']
    bz = Bugzilla(url=data['url'])
    print "Bugzilla class: %s" % bz.__class__
    if not bz.logged_in:
        if user and password:
            bz.login(user,password)
    if bz.logged_in:
        print "Logged in to bugzilla OK."
    else:
        print "Not logged in - create a .bugzillarc or provide user/password"
        # FIXME: only run some tests if .logged_in

    print "Reading product list"
    prod = bz.getproducts()
    k = sorted(prod.keys())
    print "Products found: %s, %s, %s...(%i more)" % (k[0],k[1],k[2],len(k)-3)

    print "Reading public bug (#%i)" % data['public_bug']
    print bz.getbugsimple(data['public_bug'])
    print

    print "Reading private bug (#%i)" % data['private_bug']
    try:
        print bz.getbugsimple(data['private_bug'])
    except xmlrpclib.Fault, e:
        if 'NotPermitted' in e.faultString:
            print "Failed: Not authorized."
        else:
            print "Failed: Unknown XMLRPC error: %s"  % e
    print

    print "Reading multiple bugs, one-at-a-time: %s" % str(data['bugidlist'])
    for b in data['bugidlist']:
        print bz.getbug(b)
    print

    print "Reading multiple bugs, all-at-once: %s" % str(data['bugidlist'])
    for b in bz.getbugs(data['bugidlist']):
        print b
    print

    print "Querying: %s" % str(data['query'])
    try:
        bugs = bz.query(data['query'])
        print "%s bugs found." % len(bugs)
        for bug in bugs:
            print "Bug %s" % bug
    except NotImplementedError:
        print "This bugzilla class doesn't support query()."
    print

if __name__ == '__main__':
    user = ''
    password = ''
    if len(sys.argv) > 2:
        (user,password) = sys.argv[1:3]

    print "Woo, welcome to the bugzilla.py self-test."
    for name,data in bugzillas.items():
        try:
            selftest(data,user,password)
        except KeyboardInterrupt:
            print "Exiting on keyboard interrupt."
            break
    print "Awesome. We're done."
