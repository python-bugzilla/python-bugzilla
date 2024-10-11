from types import MethodType

from bugzilla._backendrest import _BackendREST
from bugzilla._session import _BugzillaSession


class TestGetBug:
    @property
    def session(self):
        return _BugzillaSession(url="http://example.com",
                               user_agent="py-bugzilla-test",
                               sslverify=False,
                               cert=None,
                               tokencache={},
                               api_key="",
                               is_redhat_bugzilla=False)

    @property
    def backend(self):
        return _BackendREST(url="http://example.com",
                           bugzillasession=self.session)

    def test_getbug__not_permissive(self):
        backend = self.backend

        def _assertion(self, *args):
            self.assertion_called = True
            assert args and args[0] == url

        setattr(backend, "_get", MethodType(_assertion, backend))

        for _ids, aliases, url in (
                (1, None, "/bug/1"),
                ([1], [], "/bug/1"),
                (None, "CVE-1999-0001", "/bug/CVE-1999-0001"),
                ([], ["CVE-1999-0001"], "/bug/CVE-1999-0001"),
                (1, "CVE-1999-0001", "/bug"),
                ([1, 2], None, "/bug")
        ):
            backend.assertion_called = False

            backend.bug_get(_ids, aliases, {})

            assert backend.assertion_called is True

    def test_getbug__permissive(self):
        backend = self.backend

        def _assertion(self, *args):
            self.assertion_called = True
            assert args and args[0] == url and args[1] == params

        setattr(backend, "_get", MethodType(_assertion, backend))

        for _ids, aliases, url, params in (
                (1, None, "/bug", {"id": [1], "alias": None}),
                ([1], [], "/bug", {"id": [1], "alias": []}),
                (None, "CVE-1999-0001", "/bug", {"alias": ["CVE-1999-0001"], "id": None}),
                ([], ["CVE-1999-0001"], "/bug", {"alias": ["CVE-1999-0001"], "id": []}),
                (1, "CVE-1999-0001", "/bug", {"id": [1], "alias": ["CVE-1999-0001"]}),
                ([1, 2], None, "/bug", {"id": [1, 2], "alias": None})
        ):
            backend.assertion_called = False

            backend.bug_get(_ids, aliases, {"permissive": True})

            assert backend.assertion_called is True
