# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

from ._backendbase import _BackendBase
from .transport import _BugzillaXMLRPCProxy
from ._util import listify


class _BackendXMLRPC(_BackendBase):
    """
    Internal interface for direct calls to bugzilla's XMLRPC API
    """
    def __init__(self, url, bugzillasession):
        _BackendBase.__init__(self, bugzillasession)
        self._xmlrpc_proxy = _BugzillaXMLRPCProxy(url, self._bugzillasession)

    def get_xmlrpc_proxy(self):
        return self._xmlrpc_proxy

    def bugzilla_version(self):
        return self._xmlrpc_proxy.Bugzilla.version()["version"]
    def bugzilla_extensions(self):
        return self._xmlrpc_proxy.Bugzilla.extensions()

    def bug_attachment_get(self, attachment_ids, paramdict):
        data = paramdict.copy()
        data["attachment_ids"] = listify(attachment_ids)
        return self._xmlrpc_proxy.Bug.attachments(data)
    def bug_attachment_get_all(self, bug_ids, paramdict):
        data = paramdict.copy()
        data["ids"] = listify(bug_ids)
        return self._xmlrpc_proxy.Bug.attachments(data)
    def bug_attachment_create(self, paramdict):
        return self._xmlrpc_proxy.Bug.add_attachment(paramdict)
    def bug_attachment_update(self, paramdict):
        return self._xmlrpc_proxy.Bug.update_attachment(paramdict)

    def bug_comments(self, paramdict):
        return self._xmlrpc_proxy.Bug.comments(paramdict)
    def bug_create(self, paramdict):
        return self._xmlrpc_proxy.Bug.create(paramdict)
    def bug_fields(self, paramdict):
        return self._xmlrpc_proxy.Bug.fields(paramdict)
    def bug_get(self, paramdict):
        return self._xmlrpc_proxy.Bug.get(paramdict)
    def bug_history(self, paramdict):
        return self._xmlrpc_proxy.Bug.history(paramdict)
    def bug_legal_values(self, paramdict):
        return self._xmlrpc_proxy.Bug.legal_values(paramdict)
    def bug_search(self, paramdict):
        return self._xmlrpc_proxy.Bug.search(paramdict)
    def bug_update(self, paramdict):
        return self._xmlrpc_proxy.Bug.update(paramdict)
    def bug_update_tags(self, paramdict):
        return self._xmlrpc_proxy.Bug.update_tags(paramdict)

    def component_create(self, paramdict):
        return self._xmlrpc_proxy.Component.create(paramdict)
    def component_update(self, paramdict):
        return self._xmlrpc_proxy.Component.update(paramdict)

    def product_get(self, paramdict):
        return self._xmlrpc_proxy.Product.get(paramdict)
    def product_get_accessible(self):
        return self._xmlrpc_proxy.Product.get_accessible_products()
    def product_get_enterable(self):
        return self._xmlrpc_proxy.Product.get_enterable_products()
    def product_get_selectable(self):
        return self._xmlrpc_proxy.Product.get_selectable_products()

    def user_create(self, paramdict):
        return self._xmlrpc_proxy.User.create(paramdict)
    def user_get(self, paramdict):
        return self._xmlrpc_proxy.User.get(paramdict)
    def user_login(self, paramdict):
        return self._xmlrpc_proxy.User.login(paramdict)
    def user_logout(self):
        return self._xmlrpc_proxy.User.logout()
    def user_update(self, paramdict):
        return self._xmlrpc_proxy.User.update(paramdict)
