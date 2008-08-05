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

from bugzilla3 import Bugzilla3, Bugzilla32
from rhbugzilla import RHBugzilla
import xmlrpclib
import logging
log = logging.getLogger("bugzilla")

def getBugzillaClassForURL(url):
    s = xmlrpclib.ServerProxy(url)
    rhbz = False
    bzversion = ''
    c = None

    # Check for a RH-only method
    try:
        prodinfo = s.bugzilla.getProdInfo()
        rhbz = True
    except xmlrpclib.Fault:
        pass

    # Try to get the bugzilla version string
    try:
        r = s.Bugzilla.version()
        bzversion = r['version']
    except xmlrpclib.Fault:
        pass

    # current preference order: RHBugzilla, Bugzilla3
    # RH BZ 3.2 will have rhbz == True and bzversion == 3.1.x or 3.2.x. 
    # To prefer Bugzilla32 over RHBugzilla do: if rhbz and (bzversion == '')
    if rhbz:
        c = RHBugzilla
    elif bzversion.startswith('3.'):
        if bzversion.startswith('3.0'):
            c = Bugzilla3
        else: # 3.1 or higher
            c = Bugzilla32

    return c

class Bugzilla(object):
    '''Magical Bugzilla class that figures out which Bugzilla implementation
    to use and uses that.'''
    def __init__(self,**kwargs):
        if 'url' in kwargs:
            c = getBugzillaClassForURL(kwargs['url'])
            if c:
                self.__class__ = c
                c.__init__(self,**kwargs)
                log.debug("Using Bugzilla subclass: %s" % c.__name__)
        # FIXME no url? raise an error or something here, jeez
