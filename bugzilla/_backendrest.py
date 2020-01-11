# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import json
import logging
import os

from ._backendbase import _BackendBase
from .exceptions import BugzillaError


log = logging.getLogger(__name__)


# XXX remove this pylint disable
# pylint: disable=abstract-method


class _BackendREST(_BackendBase):
    """
    Internal interface for direct calls to bugzilla's REST API
    """
    def __init__(self, url, bugzillasession):
        _BackendBase.__init__(self, url, bugzillasession)
        self._bugzillasession.set_content_type("application/json")


    #########################
    # Internal REST helpers #
    #########################

    def _handle_response(self, response):
        response.raise_for_status()
        text = response.text.encode("utf-8")

        try:
            ret = dict(json.loads(text))
        except Exception:
            log.debug("Failed to parse REST response. Output is:\n%s", text)
            raise

        if ret.get("error", False):
            raise BugzillaError(ret["message"], code=ret["code"])
        return ret

    def _op(self, optype, apiurl, paramdict=None):
        fullurl = os.path.join(self._url, apiurl.lstrip("/"))
        log.debug("Bugzilla REST %s %s params=%s", optype, fullurl, paramdict)
        session = self._bugzillasession.get_requests_session()
        data = json.dumps(paramdict or {})

        if optype == "POST":
            response = session.post(fullurl, data=data)
        elif optype == "PUT":
            response = session.put(fullurl, data=data)
        else:
            response = session.get(fullurl, params=paramdict)

        return self._handle_response(response)

    def _get(self, *args, **kwargs):
        return self._op("GET", *args, **kwargs)
    def _put(self, *args, **kwargs):
        return self._op("PUT", *args, **kwargs)
    def _post(self, *args, **kwargs):
        return self._op("POST", *args, **kwargs)


    #######################
    # API implementations #
    #######################

    def get_xmlrpc_proxy(self):
        raise BugzillaError("You are using the bugzilla REST API, "
                "so raw XMLRPC access is not provided.")
    def is_rest(self):
        return True

    def bugzilla_version(self):
        return self._get("/version")
    def bugzilla_extensions(self):
        return self._get("/extensions")
