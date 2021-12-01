#
# Copyright Red Hat, Inc. 2021
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.
#

"""
Unit tests that examines custom search queries.
"""
import collections
import urllib.parse
from bugzilla.query import Q
import tests

rhbz = tests.mockbackend.make_bz(rhbz=True)


def makeurl(params):
    base_url = "https://bugzilla.redhat.com/query.cgi?"
    # sort order in regular dicts (as returned by build_query()) is not defined
    # let's sort it before comparing it to the expected URLs
    sorted_params = collections.OrderedDict(sorted(params.items()))
    return base_url + urllib.parse.urlencode(sorted_params, doseq=True)


def test_custom_search_empty_itm():
    query = rhbz.build_query(custom=Q(itm__substring="---") | Q(itm__isempty=True))
    assert (
        makeurl(query)
        == "https://bugzilla.redhat.com/query.cgi?f1=cf_internal_target_milestone&f2=cf_internal_target_milestone&j_top=OR&o1=substring&o2=isempty&query_format=advanced&v1=---"
    )


def test_custom_search_needinfo():
    query = rhbz.build_query(
        status=["NEW", "ASSIGNED", "POST", "MODIFIED", "ON_DEV", "ON_QA", "VERIFIED"],
        custom=Q(
            product__substring="Red Hat",
            requestees___login_name__anyexact=["john@redhat.com", "alice@redhat.com"],
        ),
    )
    assert (
        makeurl(query)
        == "https://bugzilla.redhat.com/query.cgi?bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&f1=product&f2=requestees.login_name&o1=substring&o2=anyexact&query_format=advanced&v1=Red+Hat&v2=john%40redhat.com%2Calice%40redhat.com"
    )


def test_custom_search_missed_deadline():
    query = rhbz.build_query(
        status=["NEW", "ASSIGNED", "POST", "MODIFIED", "ON_DEV", "ON_QA"],
        custom=Q(
            pool__substring="sst_abc_",
            cf_deadline__lessthan="today",
            cf_deadline__isnotempty=True,
        ),
    )
    assert (
        makeurl(query)
        == "https://bugzilla.redhat.com/query.cgi?bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&f1=cf_deadline&f2=cf_deadline&f3=agile_pool.name&o1=isnotempty&o2=lessthan&o3=substring&query_format=advanced&v2=today&v3=sst_abc_"
    )


def test_custom_search_stale_bugs():
    bugs_except = (
        Q(flagtypes___name__anywordssubstr=["abc+", "def+"])
        | Q(
            keywords__anywords=[
                "keyword1",
                "keyword2",
                "keyword3",
            ]
        )
        | Q(external_bugzilla___description__casesubstring="Red Hat Portal")
    )

    query = rhbz.build_query(
        status="__open__",
        custom=Q(
            ~bugs_except,
            pool__substring="sst_abc_",
            cf_final_deadline__lessthan="+30d",
            cf_final_deadline__isnotempty=None,
            cf_devel_whiteboard__notsubstring="AllowAutoClosure",
        ),
    )
    assert (
        makeurl(query)
        == "https://bugzilla.redhat.com/query.cgi?bug_status=__open__&f1=OP&f2=flagtypes.name&f3=keywords&f4=external_bugzilla.description&f5=CP&f6=cf_devel_whiteboard&f7=cf_final_deadline&f8=cf_final_deadline&f9=agile_pool.name&j1=OR&n1=1&o2=anywordssubstr&o3=anywords&o4=casesubstring&o6=notsubstring&o7=isnotempty&o8=lessthan&o9=substring&query_format=advanced&v2=abc%2B%2Cdef%2B&v3=keyword1%2Ckeyword2%2Ckeyword3&v4=Red+Hat+Portal&v6=AllowAutoClosure&v8=%2B30d&v9=sst_abc_"
    )


def test_custom_search_bugs_dev_without_dtm():
    query = rhbz.build_query(
        status="__open__",
        custom=Q(
            Q(bug_status__anyexact=["NEW", "ASSIGNED"]) | Q(cf_fixed_in__isempty=True),
            ~Q(dtm__anyexact=range(1, 10 + 1)),
            pool__substring="sst_abc_",
            cf_deadline_type__nowordssubstr=["DevCustom", "Custom"],
        ),
    )
    assert (
        makeurl(query)
        == "https://bugzilla.redhat.com/query.cgi?bug_status=__open__&f1=OP&f2=bug_status&f3=cf_fixed_in&f4=CP&f5=OP&f6=cf_dev_target_milestone&f7=CP&f8=cf_deadline_type&f9=agile_pool.name&j1=OR&j5=AND&n5=1&o2=anyexact&o3=isempty&o6=anyexact&o8=nowordssubstr&o9=substring&query_format=advanced&v2=NEW%2CASSIGNED&v6=1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10&v8=DevCustom%2CCustom&v9=sst_abc_"
    )


def test_custom_search_bugs_awaiting_verification():
    query = rhbz.build_query(
        status="__open__",
        custom=Q(
            Q(bug_status__nowordssubstr=["NEW", "ASSIGNED"])
            | Q(cf_fixed_in__isnotempty=True),
            pool__substring="sst_abc_",
            bug_status__notequals="VERIFIED",
            cf_deadline__lessthaneq="+14d",
            cf_deadline__greaterthaneq="today",
        ),
    )
    assert (
        makeurl(query)
        == "https://bugzilla.redhat.com/query.cgi?bug_status=__open__&f1=OP&f2=bug_status&f3=cf_fixed_in&f4=CP&f5=bug_status&f6=cf_deadline&f7=cf_deadline&f8=agile_pool.name&j1=OR&o2=nowordssubstr&o3=isnotempty&o5=notequals&o6=greaterthaneq&o7=lessthaneq&o8=substring&query_format=advanced&v2=NEW%2CASSIGNED&v5=VERIFIED&v6=today&v7=%2B14d&v8=sst_abc_"
    )
