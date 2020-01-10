# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import locale

from ._compatimports import IS_PY3


def listify(val):
    """Ensure that value is either None or a list, converting single values
    into 1-element lists"""
    if val is None:
        return val
    if isinstance(val, list):
        return val
    return [val]


def to_encoding(ustring):
    """
    Locale specific printing per python version
    """
    ustring = ustring or ''
    if IS_PY3:
        return str(ustring)
    else:  # pragma: no cover
        strtype = basestring  # pylint: disable=undefined-variable
        string = ustring
        if not isinstance(ustring, strtype):
            string = str(ustring)
        return string.encode(locale.getpreferredencoding(), 'replace')
