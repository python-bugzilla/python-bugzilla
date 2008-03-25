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

from bugzilla3 import Bugzilla3
from rhbugzilla import RHBugzilla
import xmlrpclib

def getBugzillaClassForURL(url):
    s = xmlrpclib.ServerProxy(url)
    # RH Bugzilla method
    prodinfo = {}
    try:
        prodinfo = s.bugzilla.getProdInfo()
        return RHBugzilla
    except xmlrpclib.Fault:
        pass

    try:
        r = s.Bugzilla.version()
        version = r['version']
        if version.startswith('3.'):
            return Bugzilla3
    except xmlrpclib.Fault:
        pass

    return None

class Bugzilla(object):
    '''Magical Bugzilla class that figures out which Bugzilla implementation
    to use and uses that.'''
    def __init__(self,**kwargs):
        if 'url' in kwargs:
            c = getBugzillaClassForURL(kwargs['url'])
            if c:
                self.__class__ = c
                c.__init__(self,**kwargs)
        # FIXME raise an error or something here, jeez
