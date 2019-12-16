# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import os
import sys
from logging import getLogger

# pylint: disable=import-error,no-name-in-module,ungrouped-imports
if sys.version_info[0] >= 3:
    from configparser import ConfigParser
else:
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
