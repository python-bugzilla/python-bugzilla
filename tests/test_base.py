from bugzilla.base import Bugzilla


def test_build_createbug():
    bz = Bugzilla(url=None)

    args = {"product": "Ubuntu 33⅓", "summary": "Hello World", "alias": "CVE-2024-0000"}
    result = bz.build_createbug(**args)
    assert result == args

    result = bz.build_createbug(groups=None, **args)
    assert result == args

    args["groups"] = []
    result = bz.build_createbug(**args)
    assert result == args

    args["groups"] += ["the-group"]
    result = bz.build_createbug(**args)
    assert result == args
