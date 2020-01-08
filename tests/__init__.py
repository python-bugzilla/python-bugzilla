# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import os


class _CLICONFIG(object):
    def __init__(self):
        self.REDHAT_URL = None
        self.REGENERATE_OUTPUT = False


CLICONFIG = _CLICONFIG()
os.environ["__BUGZILLA_UNITTEST"] = "1"
