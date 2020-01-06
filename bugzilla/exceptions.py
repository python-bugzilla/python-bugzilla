# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.


class BugzillaError(Exception):
    """
    Error raised in the Bugzilla client code.
    """
    @staticmethod
    def get_bugzilla_error_string(exc):
        """
        Helper to return the bugzilla instance error message from an
        XMLRPC Fault, or any other exception type that's raised from bugzilla
        interaction
        """
        if hasattr(exc, "faultString"):
            return getattr(exc, "faultString")
        return str(exc)

    @staticmethod
    def get_bugzilla_error_code(exc):
        """
        Helper to return the bugzilla instance error code from an
        XMLRPC Fault, or any other exception type that's raised from bugzilla
        interaction
        """
        if hasattr(exc, "faultCode"):
            return getattr(exc, "faultCode")
        return None
