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
    Class for interacting with a .bugzillatoken cache file
    """
    def __init__(self, uri, filename):
        self._filename = filename
        self._cfg = ConfigParser()
        self._domain = urlparse(uri)[1]

        if self._filename:
            self._cfg.read(self._filename)

        if self._domain not in self._cfg.sections():
            self._cfg.add_section(self._domain)

    def get_value(self):
        if self._cfg.has_option(self._domain, 'token'):
            return self._cfg.get(self._domain, 'token')
        return None

    def set_value(self, value):
        if self.get_value() == value:
            return

        if value is None:
            self._cfg.remove_option(self._domain, 'token')
        else:
            self._cfg.set(self._domain, 'token', value)

        if self._filename:
            with open(self._filename, 'w') as _cfg:
                log.debug("Saving to _cfg")
                self._cfg.write(_cfg)

    def __repr__(self):
        return '<Bugzilla Token Cache :: %s>' % self.get_value()
