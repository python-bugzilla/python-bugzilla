from types import MethodType

from bugzilla._backendrest import _BackendREST
from bugzilla._session import _BugzillaSession


def test_getbug():
    backend = _BackendREST(url="http://example.com",
                           bugzillasession=_BugzillaSession(url="http://example.com",
                                                            user_agent="py-bugzilla-test",
                                                            sslverify=False,
                                                            cert=None,
                                                            tokencache={},
                                                            api_key="",
                                                            is_redhat_bugzilla=False))

    def _assertion(self, *args, **kwargs):
        self.assertion_called = True
        assert args and args[0] == url

    backend._get = MethodType(_assertion, backend)

    for _ids, aliases, url in (
            (1, None, "/bug/1"),
            ([1], [], "/bug/1"),
            (None, "CVE-1999-0001", "/bug/CVE-1999-0001"),
            ([], ["CVE-1999-0001"], "/bug/CVE-1999-0001"),
            (1, "CVE-1999-0001", "/bug"),
    ):
        backend.assertion_called = False

        backend.bug_get(_ids, aliases, {})

        assert backend.assertion_called is True
