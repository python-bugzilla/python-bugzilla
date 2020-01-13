# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import sys

IS_PY3 = sys.version_info[0] >= 3

# pylint: disable=import-error,unused-import,ungrouped-imports
# pylint: disable=no-name-in-module
if IS_PY3:
    from collections.abc import Mapping
    from configparser import ConfigParser
    from http.cookiejar import LoadError, MozillaCookieJar
    from urllib.parse import urlparse, urlunparse, parse_qsl
    from xmlrpc.client import (Binary, DateTime, Fault, ProtocolError,
                               ServerProxy, Transport)
else:  # pragma: no cover
    from collections import Mapping
    from ConfigParser import SafeConfigParser as ConfigParser
    from cookielib import LoadError, MozillaCookieJar
    from urlparse import urlparse
    from xmlrpclib import (Binary, DateTime, Fault, ProtocolError,
                           ServerProxy, Transport)
    from urlparse import urlparse, urlunparse, parse_qsl
