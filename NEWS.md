# python-bugzilla release news

## Release 3.2.0 (January 12, 2022)
- Use soon-to-be-required Authorization header for RH bugzilla
- Remove cookie auth support

## Release 3.1.0 (July 27, 2021)
- Detect bugzilla.stage.redhat.com as RHBugzilla
- Add limit as option to build_query (Ivan Lausuch)

## Release 3.0.2 (November 12, 2020)
- Fix API key leaking into requests exceptions

## Release 3.0.1 (October 07, 2020)
- Skip man page generation to fix build on Windows (Alexander Todorov)

## Release 3.0.0 (October 03, 2020)
- Drop python2 support
- New option `bugzilla modify --minor-update option`
- requests: use PYTHONBUGZILLA_REQUESTS_TIMEOUT env variable
- xmlrpc: Don't add api key to passed in user dictionary

## Release 2.5.0 (July 04, 2020)
- cli: Add query --extrafield, --includefield, --excludefield
- Revive bugzilla.rhbugzilla.RHBugzilla import path

## Release 2.4.0 (June 29, 2020)
- Bugzilla REST API support
- Add --json command line output option
- Add APIs for Bugzilla Groups (Pierre-Yves Chibon)
- Add `Bugzilla.get_requests_session()` API to access raw requests Session
- Add `Bugzilla.get_xmlrpc_proxy()` API to access raw ServerProxy
- Add `Bugzilla requests_session=` init parameter to pass in auth, etc.
- Add `bugzilla attach --ignore-obsolete` (Čestmír Kalina)
- Add `bugzilla login --api-key` for API key prompting (Danilo C. L. de
  Paula)
- Add `bugzilla new --private`

## Release 2.3.0 (August 26, 2019)
- restrict-login suppot (Viliam Krizan)
- cli: Add support for private attachments (Brian 'Redbeard' Harrington)
- Fix python3 deprecation warnings
- Drop python 3.3 support, minimum python3 is python 3.4 now

## Release 2.2.0 (August 11, 2018)
- Port tests to pytest
- cli: --cert Client side certificate support (Tobias Wolter)
- cli: add ability to post comment while sending attachment (Jeff Mahoney)
- cli: Add --comment-tag option
- cli: Add info --active-components
- Add a raw Product.get wrapper API

## Release 2.1.0 (March 30, 2017)
- Support for bugzilla 5 API Keys (Dustin J. Mitchell)
- bugzillarc can be used to set default URL for the cli tool
- Revive update_flags wrapper
- Bug fixes and minor improvements

## Release 2.0.0 (Feb 08 2017)

This release contains several small to medium API breaks. I expect most users
won't notice any difference. I previously outlined the changes here:

https://lists.fedorahosted.org/archives/list/python-bugzilla@lists.fedorahosted.org/thread/WCYPOKJZFYOW7RRT44FCM5GQU26O56K4/

The major changes are:

- Several fixes for use with bugzilla 5
- Bugzilla.bug_autorefresh now defaults to False
- Credentials are now cached in ~/.cache/python-bugzilla/
- bin/bugzilla was converted to argparse
- bugzilla query --boolean_chart option is removed
- Unify command line flags across sub commands

## Release 1.2.2 (Sep 23 2015)

- Switch hosting to http://github.com/python-bugzilla/python-bugzilla
- Fix requests usage when ndg-httpsclient is installed (Arun Babu
  Neelicattu)
- Add non-rhbz support for getting bug comments (AJ Lewis)
- Misc bugfixes and improvements

## Release 1.2.1 (May 22 2015)

- bin/bugzilla: Add --ensure-logged-in option
- Fix get_products with bugzilla.redhat.com
- A few other minor improvements

## Release 1.2.0 (Apr 08 2015)

- Add bugzilla new/query/modify --field flag (Arun Babu Neelicattu)
- API support for ExternalBugs (Arun Babu Neelicattu, Brian Bouterse)
- Add new/modify --alias support (Adam Williamson)
- Bugzilla.logged_in now returns live state (Arun Babu Neelicattu)
- Fix getbugs API with latest Bugzilla releases

## Release 1.1.0 (Jun 01 2014)

- Support for bugzilla tokens (Arun Babu Nelicattu)
- bugzilla: Add query/modify --tags
- bugzilla --login: Allow to login and run a command in one shot
- bugzilla --no-cache-credentials: Don't use or save cached credentials
  when using the CLI
- Show bugzilla errors when login fails
- Don't pull down attachments in bug.refresh(), need to get
  bug.attachments manually
- Add Bugzilla bug_autorefresh parameter.

## Release 1.0.0 (Mar 25 2014)

- Python 3 support (Arun Babu Neelicattu)
- Port to python-requests (Arun Babu Neelicattu)
- bugzilla: new: Add --keywords, --assigned_to, --qa_contact (Lon Hohberger)
- bugzilla: query: Add --quicksearch, --savedsearch
- bugzilla: query: Support saved searches with --from-url
- bugzilla: --sub-component support for all relevant commands

## Release 0.9.0 (Jun 19 2013)

- CVE-2013-2191: Switch to pycurl to get SSL host and cert validation
- bugzilla: modify: add --dependson (Don Zickus)
- bugzilla: new: add --groups option (Paul Frields)
- bugzilla: modify: Allow setting nearly every bug parameter
- NovellBugzilla implementation removed, can't get it to work

## Release 0.8.0 (Feb 16 2013)

- Replace usage of non-upstream Red Hat bugzilla APIs with upstream replacements
- Test suite improvements, nearly complete code coverage
- Fix all open bug reports and RFEs
