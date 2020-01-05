# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import os
import sys
from logging import getLogger

# pylint: disable=import-error,no-name-in-module,ungrouped-imports
if sys.version_info[0] >= 3:
    from configparser import ConfigParser
    from urllib.parse import urlparse  # pylint: disable=no-name-in-module
else:
    from urlparse import urlparse
    from ConfigParser import SafeConfigParser as ConfigParser
# pylint: enable=import-error,no-name-in-module,ungrouped-imports

from ._util import listify

log = getLogger(__name__)

DEFAULT_CONFIGPATHS = [
    '/etc/bugzillarc',
    '~/.bugzillarc',
    '~/.config/python-bugzilla/bugzillarc',
]


def open_bugzillarc(configpaths=-1):
    if configpaths == -1:
        configpaths = DEFAULT_CONFIGPATHS[:]

    # pylint: disable=protected-access
    configpaths = [os.path.expanduser(p) for p in
                   listify(configpaths)]
    # pylint: enable=protected-access
    cfg = ConfigParser()
    read_files = cfg.read(configpaths)
    if not read_files:
        return

    log.info("Found bugzillarc files: %s", read_files)
    return cfg


class _BugzillaTokenCache(object):
    """
    Cache for tokens, including, with apologies for the duplicative
    terminology, both Bugzilla Tokens and API Keys.
    """

    def __init__(self, uri, tokenfilename):
        self.tokenfilename = tokenfilename
        self.tokenfile = ConfigParser()
        self.domain = urlparse(uri)[1]

        if self.tokenfilename:
            self.tokenfile.read(self.tokenfilename)

        if self.domain not in self.tokenfile.sections():
            self.tokenfile.add_section(self.domain)

    @property
    def value(self):
        if self.tokenfile.has_option(self.domain, 'token'):
            return self.tokenfile.get(self.domain, 'token')
        else:
            return None

    @value.setter
    def value(self, value):
        if self.value == value:
            return

        if value is None:
            self.tokenfile.remove_option(self.domain, 'token')
        else:
            self.tokenfile.set(self.domain, 'token', value)

        if self.tokenfilename:
            with open(self.tokenfilename, 'w') as tokenfile:
                log.debug("Saving to tokenfile")
                self.tokenfile.write(tokenfile)

    def __repr__(self):
        return '<Bugzilla Token Cache :: %s>' % self.value
