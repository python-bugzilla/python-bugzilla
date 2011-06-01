# python-bugzilla - a Python interface to bugzilla using xmlrpclib.
#
# Copyright (C) 2007,2008 Red Hat Inc.
# Author: Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

from bugzilla3 import Bugzilla3, Bugzilla32, Bugzilla34, Bugzilla36
from rhbugzilla import RHBugzilla, RHBugzilla3
from nvlbugzilla import NovellBugzilla
from base import version
import xmlrpclib
import logging
log = logging.getLogger("bugzilla")

# advertised class list
classlist = ['Bugzilla3', 'Bugzilla32', 'Bugzilla34', 'Bugzilla36',
             'RHBugzilla3', 'NovellBugzilla']

def getBugzillaClassForURL(url):
    log.debug("Choosing subclass for %s" % url)
    s = xmlrpclib.ServerProxy(url)
    rhbz = False
    bzversion = ''
    c = None

    # Check for a RH-only method
    try:
        log.debug("Checking for RH Bugzilla method bugzilla.getProdInfo()")
        prodinfo = s.bugzilla.getProdInfo()
        rhbz = True
    except xmlrpclib.Fault:
        pass
    log.debug("rhbz=%s" % str(rhbz))

    # Try to get the bugzilla version string
    try:
        log.debug("Checking return value of Buzilla.version()")
        r = s.Bugzilla.version()
        bzversion = r['version']
    except xmlrpclib.Fault:
        pass
    log.debug("bzversion='%s'" % str(bzversion))

    # XXX note preference order: RHBugzilla* wins if available
    # RH BZ 3.2 will have rhbz == True and bzversion == 3.1.x or 3.2.x.
    if rhbz:
        if bzversion.startswith('3.'):
            c = RHBugzilla3
        else:
            c = RHBugzilla
    elif bzversion.startswith('3.'):
        if bzversion.startswith('3.6'):
            c = Bugzilla36
        elif bzversion.startswith('3.4'):
            c = Bugzilla34
        elif bzversion.startswith('3.2'):
            c = Bugzilla32
        else:
            c = Bugzilla3

    return c

class Bugzilla(object):
    '''Magical Bugzilla class that figures out which Bugzilla implementation
    to use and uses that. Requires 'url' parameter so we can check available
    XMLRPC methods to determine the Bugzilla version.'''
    def __init__(self,**kwargs):
        log.info("Bugzilla v%s initializing" % base.version)
        if 'url' in kwargs:
            c = getBugzillaClassForURL(kwargs['url'])
            if c:
                self.__class__ = c
                c.__init__(self,**kwargs)
                log.info("Chose subclass %s v%s" % (c.__name__,c.version))
            else:
                raise ValueError, "Couldn't determine Bugzilla version for %s" % kwargs['url']
        else:
            raise TypeError, "You must pass a valid bugzilla xmlrpc.cgi URL"
