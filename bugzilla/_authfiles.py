# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import os
from logging import getLogger

from ._compatimports import (ConfigParser, LoadError,
                            MozillaCookieJar, urlparse)
from .exceptions import BugzillaError
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


def _parse_hostname(url):
    # If http://example.com is passed, netloc=example.com path=""
    # If just example.com is passed, netloc="" path=example.com
    parsedbits = urlparse(url)
    return parsedbits.netloc or parsedbits.path


def _default_location(filename, kind):
    """
    Determine default location for filename, like 'bugzillacookies'. If
    old style ~/.bugzillacookies exists, we use that, otherwise we
    use ~/.cache/python-bugzilla/bugzillacookies.
    Same for bugzillatoken and bugzillarc
    """
    homepath = os.path.expanduser("~/.%s" % filename)
    xdgpath = os.path.expanduser("~/.%s/python-bugzilla/%s" % (kind, filename))
    if os.path.exists(xdgpath):
        return xdgpath
    if os.path.exists(homepath):
        return homepath

    if not os.path.exists(os.path.dirname(xdgpath)):
        os.makedirs(os.path.dirname(xdgpath), 0o700)
    return xdgpath


def _default_cache_location(filename):
    return _default_location(filename, 'cache')


def _default_config_location(filename):
    return _default_location(filename, 'config')


def _save_api_key(url, api_key, configpaths):
    """
    Save the API_KEY in the config file.

    If tokenfile and cookiefile are undefined, it means that the
    API was called with --no-cache-credentials and no change will be
    made
    """
    if configpaths:
        config_filename = configpaths[0]
    else:
        config_filename = _default_config_location('bugzillarc')
    section = _parse_hostname(url)

    cfg = ConfigParser()
    cfg.read(config_filename)

    if section not in cfg.sections():
        cfg.add_section(section)

    cfg.set(section, 'api_key', api_key.strip())

    with open(config_filename, 'w') as configfile:
        cfg.write(configfile)

    log.info("API key written to %s", config_filename)
    print("API key written to %s" % config_filename)


def _build_cookiejar(cookiefile):
    cj = MozillaCookieJar(cookiefile)
    if cookiefile is None:
        return cj
    if not os.path.exists(cookiefile):
        # Make sure a new file has correct permissions
        open(cookiefile, 'a').close()
        os.chmod(cookiefile, 0o600)
        cj.save()
        return cj

    try:
        cj.load()
        return cj
    except LoadError:
        raise BugzillaError("cookiefile=%s not in Mozilla format" %
                            cookiefile)
