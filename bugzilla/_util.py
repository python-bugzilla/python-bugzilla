# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.


def listify(val):
    """Ensure that value is either None or a list, converting single values
    into 1-element lists"""
    if val is None:
        return val
    if isinstance(val, list):
        return val
    return [val]
