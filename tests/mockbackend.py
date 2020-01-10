# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import inspect

import bugzilla
from bugzilla._backendbase import _BackendBase

import tests.utils


# pylint: disable=abstract-method,arguments-differ


class BackendMock(_BackendBase):
    _version = None
    _extensions = None

    def bugzilla_version(self):
        return {"version": self._version}
    def bugzilla_extensions(self):
        return self._extensions

    def __helper(self, args):
        # Grab the calling function name and use it to generate
        # input and output variable names for the class. So if this
        # is called from bug_get, we look for:
        #   self._bug_get_args
        #   self._bug_get_return
        prevfuncname = inspect.stack()[1][3]
        func_args = getattr(self, "_%s_args" % prevfuncname)
        func_return = getattr(self, "_%s_return" % prevfuncname)
        if isinstance(func_return, BaseException):
            raise func_return

        if isinstance(func_args, dict):
            print(args[-1])
            assert func_args == args[-1]
        elif func_args is not None:
            tests.utils.diff_compare(args[-1], func_args)

        if isinstance(func_return, dict):
            return func_return

        returnstr = open(tests.utils.tests_path(func_return)).read()
        return eval(returnstr)  # pylint: disable=eval-used

    def bug_attachment_create(self, *args):
        return self.__helper(args)
    def bug_attachment_get(self, *args):
        return self.__helper(args)
    def bug_attachment_get_all(self, *args):
        return self.__helper(args)
    def bug_attachment_update(self, *args):
        return self.__helper(args)

    def bug_create(self, *args):
        return self.__helper(args)
    def bug_legal_values(self, *args):
        return self.__helper(args)
    def bug_get(self, *args):
        return self.__helper(args)
    def bug_search(self, *args):
        return self.__helper(args)
    def bug_update(self, *args):
        return self.__helper(args)
    def bug_update_tags(self, *args):
        return self.__helper(args)

    def externalbugs_add(self, *args):
        return self.__helper(args)
    def externalbugs_update(self, *args):
        return self.__helper(args)
    def externalbugs_remove(self, *args):
        return self.__helper(args)

    def product_get(self, *args):
        return self.__helper(args)
    def product_get_accessible(self, *args):
        return self.__helper(args)

    def user_create(self, *args):
        return self.__helper(args)
    def user_get(self, *args):
        return self.__helper(args)
    def user_login(self, *args):
        return self.__helper(args)
    def user_logout(self, *args):
        return self.__helper(args)
    def user_update(self, *args):
        return self.__helper(args)


def _make_backend_class(version="6.0.0", extensions=None,
        rhbz=False, **kwargs):
    if not extensions:
        extensions = {"extensions": {"foo": {"version": "0.01"}}}
    if rhbz:
        extensions["extensions"]['RedHat'] = {'version': '0.3'}

    class TmpBackendClass(BackendMock):
        _version = version
        _extensions = extensions

    for key, val in kwargs.items():
        setattr(TmpBackendClass, "_%s" % key, val)

    return TmpBackendClass


def make_bz(bz_kwargs=None, **kwargs):
    bz_kwargs = (bz_kwargs or {}).copy()
    if "url" in bz_kwargs:
        raise RuntimeError("Can't set 'url' in mock make_bz, use connect()")

    if "use_creds" not in bz_kwargs:
        bz_kwargs["use_creds"] = False
    bz = bugzilla.Bugzilla(url=None, **bz_kwargs)
    backendclass = _make_backend_class(**kwargs)
    # pylint: disable=protected-access
    bz._get_backend_class = lambda *a, **k: backendclass
    bz.connect("https:///TESTSUITEMOCK")
    return bz
