# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import inspect

import bugzilla
from bugzilla._backendbase import _BackendBase

import tests.utils


# pylint: disable=abstract-method,arguments-differ


class BackendMock(_BackendBase):
    _version = None

    def bugzilla_version(self):
        return {"version": self._version}

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

        filename = None
        expect_out = func_args
        if isinstance(func_args, str):
            filename = func_args
            expect_out = None

        # Hack to strip out attachment content from the generated
        # test output, because it doesn't play well with the test
        # suite running on python2
        if "content-disposition" in str(args):
            largs = list(args)
            largs[1] = "STRIPPED-BY-TESTSUITE"
            args = tuple(largs)

        if filename or expect_out:
            tests.utils.diff_compare(args, filename, expect_out)

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

    def bug_comments(self, *args):
        return self.__helper(args)
    def bug_create(self, *args):
        return self.__helper(args)
    def bug_history(self, *args):
        return self.__helper(args)
    def bug_get(self, *args):
        return self.__helper(args)
    def bug_fields(self, *args):
        return self.__helper(args)
    def bug_search(self, *args):
        return self.__helper(args)
    def bug_update(self, *args):
        return self.__helper(args)
    def bug_update_tags(self, *args):
        return self.__helper(args)

    def component_create(self, *args):
        return self.__helper(args)
    def component_get(self, *args):
        return self.__helper(args)
    def component_update(self, *args):
        return self.__helper(args)

    def group_get(self, *args):
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
    def product_get_enterable(self, *args):
        return self.__helper(args)
    def product_get_selectable(self, *args):
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


def _make_backend_class(version="6.0.0", **kwargs):

    class TmpBackendClass(BackendMock):
        _version = version

    for key, val in kwargs.items():
        setattr(TmpBackendClass, "_%s" % key, val)

    return TmpBackendClass


def make_bz(bz_kwargs=None, rhbz=False, **kwargs):
    bz_kwargs = (bz_kwargs or {}).copy()
    if "url" in bz_kwargs:
        raise RuntimeError("Can't set 'url' in mock make_bz, use connect()")

    if "use_creds" not in bz_kwargs:
        bz_kwargs["use_creds"] = False

    bz = bugzilla.Bugzilla(url=None, **bz_kwargs)
    backendclass = _make_backend_class(**kwargs)

    def _get_backend_class(url):
        return backendclass, bugzilla.Bugzilla.fix_url(url)

    # pylint: disable=protected-access
    bz._get_backend_class = _get_backend_class

    url = "https:///TESTSUITEMOCK"
    if rhbz:
        url += "?fakeredhat=bugzilla.redhat.com"
    bz.connect(url)
    return bz
