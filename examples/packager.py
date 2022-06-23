#!/usr/bin/python3
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

# packager.py
# CLI BZ routines for stuff that I do

from argparse import ArgumentParser
import bugzilla
import sys


def main():

    parser = ArgumentParser(prog="rhbz")

    # flags to set behavior
    parser.add_argument(
        "-e",
        "--epel",
        action="store_true",
        dest="epel",
        help="bool: file against EPEL product",
        default=False,
    )

    # flags to set behavior
    parser.add_argument(
        "-n",
        "--newpackage",
        action="store_true",
        dest="newpackage",
        help="bool: submit a new package for review",
        default=False,
    )

    # variables
    parser.add_argument(
        "-c",
        "--component",
        required=True,
        dest="component",
        help="file against this component (usually a package)",
        type=str,
    )

    parser.add_argument(
        "-p",
        "--packager",
        dest="packager",
        help="FAS if reporter is Fedora packager",
    )

    args = parser.parse_args()

    # some sanity checks
    if args.epel and args.newpackage:
        sys.exit("\nCannot submit package for review and request in EPEL. Exiting.")

    # bugzilla instance and login (it's all that I use, so hardcode for now)
    URL = "bugzilla.redhat.com"
    bzapi = bugzilla.Bugzilla(URL)
    if not bzapi.logged_in:
        print(f"Cached login credentials are required for {URL}")
        # using API keys as standard now over username/password
        bzapi.interactive_save_api_key()

    # template our query
    query = bzapi.build_query(
        component=args.component,
        product=f"Fedora{args.epel*' EPEL'}",
        include_fields=["id", "summary"],
    )

    # when requesting EPEL, check for open;
    # new package request should search everything
    if args.epel:
        query["status"] = "OPEN"

    # run query and print findings
    bugs = bzapi.query(query)
    # print(f"Found {len(bugs)} bugs with our query")
    for bug in bugs:
        print(bug.id, bug.summary)

    # complete procedure to request build in EPEL
    # see https://docs.fedoraproject.org/en-US/epel/epel-package-request/
    if args.epel:
        print(
            f"Review the preceding results: if {args.component} already requested, kill this with Ctrl+D"
        )
        input("If nothing looks like an EPEL request, press Enter to continue...")

        release = "epel9"

        createinfo = bzapi.build_createbug(
            product="Fedora EPEL",
            version=release,
            component=args.component,
            summary=f"Please branch and build {args.component} in {release}",
        )

        if args.packager:
            createinfo[
                "description"
            ] = f"""
            Please branch and build {args.component} in {release}.

            If you do not wish to maintain {args.component} in {release},
            or do not think you will be able to do this in a timely manner,
            I would be happy to be a co-maintainer of the package (FAS {args.packager});
            please add me through https://src.fedoraproject.org/rpms/{args.component}/adduser
            """
        else:
            createinfo[
                "description"
            ] = f"Please branch and build {args.component} in {release}"

    if args.newpackage:
        if not (len(bugs) == 0):
            print(f"Something matched the search for {args.component}")
            print(f"If {args.component} already exists, exit now with Ctrl+D")
            input("Otherwise, to file the review request, press Enter to continue...")

        release = "rawhide"

        summary = input("Enter a (very) short package summary: ")
        url_spec = input("Enter the spec URL: ")
        url_srpm = input("Enter the SRPM URL: ")

        createinfo = bzapi.build_createbug(
            product="Fedora",
            version=release,
            component="Package Review",
            summary=f"Review Request:  {args.component} - {summary}",
            description=f"""
            Spec URL: {url_spec}
            SRPM URL: {url_srpm}
            Description: {summary}
            Fedora Account System Username: {args.packager}
            """,
        )

    newbug = bzapi.createbug(createinfo)
    print(f"Created new bug id={newbug.id} url={newbug.weburl}")


if __name__ == "__main__":
    main()
