# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import os
from logging import getLogger

from ._compatimports import (ConfigParser, LoadError,
                            MozillaCookieJar, urlparse)
from .exceptions import BugzillaError
from ._util import listify

log = getLogger(__name__)


def _parse_hostname(url):
    # If http://example.com is passed, netloc=example.com path=""
    # If just example.com is passed, netloc="" path=example.com
    parsedbits = urlparse(url)
    return parsedbits.netloc or parsedbits.path


def _makedirs(path):
    if os.path.exists(os.path.dirname(path)):
        return
    os.makedirs(os.path.dirname(path), 0o700)


def _default_location(filename, kind):
    """
    Determine default location for passed filename and xdg kind,
    example: ~/.cache/python-bugzilla/bugzillacookies
    """
    xdgpath = os.path.expanduser("~/.%s/python-bugzilla/%s" % (kind, filename))
    return xdgpath


def _default_cache_location(filename):
    return _default_location(filename, 'cache')


class _BugzillaRCFile(object):
    """
    Helper class for interacting with bugzillarc files
    """
    @staticmethod
    def get_default_configpaths():
        paths = [
            '/etc/bugzillarc',
            '~/.bugzillarc',
            '~/.config/python-bugzilla/bugzillarc',
        ]
        return paths

    def __init__(self):
        self._cfg = None
        self._configpaths = None
        self.set_configpaths(None)

    def set_configpaths(self, configpaths):
        configpaths = [os.path.expanduser(p) for p in
                       listify(configpaths or [])]

        cfg = ConfigParser()
        read_files = cfg.read(configpaths)
        if read_files:
            log.info("Found bugzillarc files: %s", read_files)

        self._cfg = cfg
        self._configpaths = configpaths or []

    def get_configpaths(self):
        return self._configpaths[:]

    def get_default_url(self):
        """
        Grab a default URL from bugzillarc [DEFAULT] url=X
        """
        cfgurl = self._cfg.defaults().get("url", None)
        if cfgurl is not None:
            log.debug("bugzillarc: found cli url=%s", cfgurl)
            return cfgurl

    def parse(self, url):
        """
        Find the section for the passed URL domain, and return all the fields
        """
        section = ""
        log.debug("bugzillarc: Searching for config section matching %s", url)

        urlhost = _parse_hostname(url)
        for sectionhost in sorted(self._cfg.sections()):
            # If the section is just a hostname, make it match
            # If the section has a / in it, do a substring match
            if "/" not in sectionhost:
                if sectionhost == urlhost:
                    section = sectionhost
            elif sectionhost in url:
                section = sectionhost
            if section:
                log.debug("bugzillarc: Found matching section: %s", section)
                break

        if not section:
            log.debug("bugzillarc: No section found")
            return {}
        return dict(self._cfg.items(section))


    def save_api_key(self, url, api_key):
        """
        Save the API_KEY in the config file. We use the last file
        in the configpaths list, which is the one with the highest
        precedence.
        """
        configpaths = self.get_configpaths()
        if not configpaths:
            return None

        config_filename = configpaths[-1]
        section = _parse_hostname(url)
        cfg = ConfigParser()
        cfg.read(config_filename)

        if section not in cfg.sections():
            cfg.add_section(section)

        cfg.set(section, 'api_key', api_key.strip())

        _makedirs(config_filename)
        with open(config_filename, 'w') as configfile:
            cfg.write(configfile)

        return config_filename


class _BugzillaTokenCache(object):
    """
    Class for interacting with a .bugzillatoken cache file
    """
    @staticmethod
    def get_default_path():
        return _default_cache_location("bugzillatoken")

    def __init__(self):
        self._filename = None
        self._cfg = None

    def _get_domain(self, url):
        domain = urlparse(url)[1]
        if domain and domain not in self._cfg.sections():
            self._cfg.add_section(domain)
        return domain

    def get_value(self, url):
        domain = self._get_domain(url)
        if self._cfg.has_option(domain, 'token'):
            return self._cfg.get(domain, 'token')
        return None

    def set_value(self, url, value):
        if self.get_value(url) == value:
            return

        domain = self._get_domain(url)
        if value is None:
            self._cfg.remove_option(domain, 'token')
        else:
            self._cfg.set(domain, 'token', value)

        if self._filename:
            _makedirs(self._filename)
            with open(self._filename, 'w') as _cfg:
                log.debug("Saving to _cfg")
                self._cfg.write(_cfg)

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        log.debug("Using tokenfile=%s", filename)
        cfg = ConfigParser()
        if filename:
            cfg.read(filename)
        self._filename = filename
        self._cfg = cfg


class _BugzillaCookieCache(object):
    @staticmethod
    def get_default_path():
        return _default_cache_location("bugzillacookies")

    def __init__(self):
        self._cookiejar = None

    def _build_cookiejar(self, cookiefile):
        cj = MozillaCookieJar(cookiefile)
        if (cookiefile is None or
            not os.path.exists(cookiefile)):
            return cj

        try:
            cj.load()
            return cj
        except LoadError:
            raise BugzillaError("cookiefile=%s not in Mozilla format" %
                                cookiefile)

    def set_filename(self, cookiefile):
        log.debug("Using cookiefile=%s", cookiefile)
        self._cookiejar = self._build_cookiejar(cookiefile)

    def get_filename(self):
        return self._cookiejar.filename

    def get_cookiejar(self):
        return self._cookiejar

    def set_cookies(self, cookies):
        for cookie in cookies:
            self._cookiejar.set_cookie(cookie)

        cookiefile = self._cookiejar.filename
        if not cookiefile:
            return

        if not os.path.exists(cookiefile):
            _makedirs(cookiefile)
            # Make sure a new file has correct permissions
            open(cookiefile, 'a').close()
            os.chmod(cookiefile, 0o600)

        self._cookiejar.save()
