========
bugzilla
========

-----------------------------------------------
command line tool for interacting with Bugzilla
-----------------------------------------------

:Manual section: 1
:Manual group: User Commands


SYNOPSIS
========

**bugzilla** [*options*] [*command*] [*command-options*]


DESCRIPTION
===========

**bugzilla** is a command line tool for interacting with a Bugzilla
instance over REST or XMLRPC.

|
| *command* is one of:
| * login - log into the given bugzilla instance
| * new - create a new bug
| * query - search for bugs matching given criteria
| * modify - modify existing bugs
| * attach - attach files to existing bugs, or get attachments
| * info - get info about the given bugzilla instance


GLOBAL OPTIONS
--------------

- ``--help, -h``

show this help message and exit

- ``--bugzilla=BUGZILLA``

The bugzilla URL. Full API URLs are typically like:

|
| * https://bugzilla.example.com/xmlrpc.cgi    # XMLRPC API
| * https://bugzilla.example.com/rest/         # REST API
|

If a non-specific URL is passed, like 'bugzilla.redhat.com', **bugzilla**
will try to probe whether the expected XMLRPC or REST path is available,
preferring XMLRPC for backwards compatibility.

The default URL https://bugzilla.redhat.com

- ``--nosslverify``

Don't error on invalid bugzilla SSL certificate

- ``--cert=CERTFILE``

client side certificate file needed by the webserver.

- ``--login``

Run interactive "login" before performing the specified command.

- ``--username=USERNAME``

Log in with this username

- ``--password=PASSWORD``

Log in with this password

- ``--restrict-login``

The session (login token) will be restricted to the current IP
address.

- ``--ensure-logged-in``

Raise an error if we aren't logged in to bugzilla. Consider using
this if you are depending on cached credentials, to ensure that when
they expire the tool errors, rather than subtly change output.

- ``--no-cache-credentials``

Don't save any bugzilla cookies or tokens to disk, and don't use any
pre-existing credentials.

- ``--cookiefile=COOKIEFILE``

cookie file to use for bugzilla authentication

- ``--tokenfile=TOKENFILE``

token file to use for bugzilla authentication

- ``--verbose``

give more info about what's going on

- ``--debug``

output bunches of debugging info

- ``--version``

show program's version number and exit


Standard bugzilla options
=========================

These options are shared by some combination of the 'new', 'query', and
'modify' sub commands. Not every option works for each command though.

- ``--product=PRODUCT, -p PRODUCT``

Product name

- ``--version=VERSION, -v VERSION``

Product version

- ``--component=COMPONENT, -c COMPONENT``

Component name

- ``--summary=SUMMARY, -s SUMMARY, --short_desc=SUMMARY``

Bug summary

- ``--comment=DESCRIPTION, -l DESCRIPTION``

Set initial bug comment/description

- ``--comment-tag=TAG``

Comment tag for the new comment

- ``--sub-component=SUB_COMPONENT``

RHBZ sub component name

- ``--os=OS, -o OS``

Operating system

- ``--arch=ARCH``

Arch this bug occurs on

- ``--severity=SEVERITY, -x SEVERITY``

Bug severity

- ``--priority=PRIORITY, -z PRIORITY``

Bug priority

- ``--alias=ALIAS``

Bug alias (name)

- ``--status=STATUS, -s STATUS, --bug_status=STATUS``

Bug status (NEW, ASSIGNED, etc.)

- ``--url=URL, -u URL``

URL for further bug info

- ``--target_milestone=TARGET_MILESTONE, -m TARGET_MILESTONE``

Target milestone

- ``--target_release=TARGET_RELEASE``

RHBZ Target release

- ``--blocked=BUGID[, BUGID, ...]``

Bug IDs that this bug blocks

- ``--dependson=BUGID[, BUGID, ...]``

Bug IDs that this bug depends on

- ``--keywords=KEYWORD[, KEYWORD, ...]``

Bug keywords

- ``--groups=GROUP[, GROUP, ...]``

Which user groups can view this bug

- ``--cc=CC[, CC, ...]``

CC list

- ``--assigned_to=ASSIGNED_TO, -a ASSIGNED_TO, --assignee ASSIGNED_TO``

Bug assignee

- ``--qa_contact=QA_CONTACT, -q QA_CONTACT``

QA contact

- ``--flag=FLAG``

Set or unset a flag. For example, to set a flag named devel_ack, do
--flag devel_ack+ Unset a flag with the 'X' value, like --flag
needinfoX

- ``--tags=TAG``

Set (personal) tags field

- ``--whiteboard WHITEBOARD, -w WHITEBOARD, --status_whiteboard WHITEBOARD``

Whiteboard field

- ``--devel_whiteboard DEVEL_WHITEBOARD``

RHBZ devel whiteboard field

- ``--internal_whiteboard INTERNAL_WHITEBOARD``

RHBZ internal whiteboard field

- ``--qa_whiteboard QA_WHITEBOARD``

RHBZ QA whiteboard field

- ``--fixed_in FIXED_IN, -F FIXED_IN``

RHBZ 'Fixed in version' field

- ``--field=FIELD=VALUE``

Manually specify a bugzilla API field. FIELD is the raw name used
by the bugzilla instance. For example if your bugzilla instance has a
custom field cf_my_field, do: --field cf_my_field=VALUE


Output options
==============

These options are shared by several commands, for tweaking the text
output of the command results.

- ``--full, -f``

output detailed bug info

- ``--ids, -i``

output only bug IDs

- ``--extra, -e``

output additional bug information (keywords, Whiteboards, etc.)

- ``--oneline``

one line summary of the bug (useful for scripts)

- ``--json``

output bug contents in JSON format

- ``--raw``

raw output of the bugzilla contents. This format is unstable and
difficult to parse. Please use the ``--json`` instead if you want
maximum output from the `bugzilla`

- ``--outputformat=OUTPUTFORMAT``

Print output in the form given. You can use RPM-style tags that match
bug fields, e.g.: '%{id}: %{summary}'.

The output of the bugzilla tool should NEVER BE PARSED unless you are
using a custom --outputformat. For everything else, just don't parse it,
the formats are not stable and are subject to change.

--outputformat allows printing arbitrary bug data in a user preferred
format. For example, to print a returned bug ID, component, and product,
separated with ::, do:

--outputformat "%{id}::%{component}::%{product}"

The fields (like 'id', 'component', etc.) are the names of the values
returned by bugzilla's API. To see a list of all fields,
check the API documentation in the 'SEE ALSO' section. Alternatively,
run a 'bugzilla --debug query ...' and look at the key names returned in
the query results. Also, in most cases, using the name of the associated
command line switch should work, like --bug_status becomes
%{bug_status}, etc.


‘query’ specific options
========================

Certain options can accept a comma separated list to query multiple
values, including --status, --component, --product, --version, --id.

Note: querying via explicit command line options will only get you so
far. See the --from-url option for a way to use powerful Web UI queries
from the command line.

- ``--id ID, -b ID, --bug_id ID``

specify individual bugs by IDs, separated with commas

- ``--reporter REPORTER, -r REPORTER``

Email: search reporter email for given address

- ``--quicksearch QUICKSEARCH``

Search using bugzilla's quicksearch functionality.

- ``--savedsearch SAVEDSEARCH``

Name of a bugzilla saved search. If you don't own this saved search,
you must passed --savedsearch_sharer_id.

- ``--savedsearch-sharer-id SAVEDSEARCH_SHARER_ID``

Owner ID of the --savedsearch. You can get this ID from the URL
bugzilla generates when running the saved search from the web UI.

- ``--from-url WEB_QUERY_URL``

Make a working query via bugzilla's 'Advanced search' web UI, grab
the url from your browser (the string with query.cgi or buglist.cgi
in it), and --from-url will run it via the bugzilla API. Don't forget
to quote the string! This only works for Bugzilla 5 and Red Hat
bugzilla


‘modify’ specific options
=========================

Fields that take multiple values have a special input format.

| Append: --cc=foo@example.com
| Overwrite: --cc==foo@example.com
| Remove: --cc=-foo@example.com

Options that accept this format: --cc, --blocked, --dependson, --groups,
--tags, whiteboard fields.

- ``--close RESOLUTION, -k RESOLUTION``

Close with the given resolution (WONTFIX, NOTABUG, etc.)

- ``--dupeid ORIGINAL, -d ORIGINAL``

ID of original bug. Implies --close DUPLICATE

- ``--private``

Mark new comment as private

- ``--reset-assignee``

Reset assignee to component default

- ``--reset-qa-contact``

Reset QA contact to component default


‘new’ specific options
======================

- ``--private``

Mark new comment as private


‘attach’ options
================

- ``--file=FILENAME, -f FILENAME``

File to attach, or filename for data provided on stdin

- ``--description=DESCRIPTION, -d DESCRIPTION``

A short description of the file being attached

- ``--type=MIMETYPE, -t MIMETYPE``

Mime-type for the file being attached

- ``--get=ATTACHID, -g ATTACHID``

Download the attachment with the given ID

- ``--getall=BUGID, --get-all=BUGID``

Download all attachments on the given bug

- ``--ignore-obsolete``

Do not download attachments marked as obsolete.

- ``--comment=COMMENT, -l COMMENT``

Add comment with attachment


‘info’ options
==============

- ``--products, -p``

Get a list of products

- ``--components=PRODUCT, -c PRODUCT``

List the components in the given product

- ``--component_owners=PRODUCT, -o PRODUCT``

List components (and their owners)

- ``--versions=PRODUCT, -v PRODUCT``

List the versions for the given product

- ``--active-components``

Only show active components. Combine with --components*


AUTHENTICATION CACHE AND API KEYS
=================================

Some command usage will require an active login to the bugzilla
instance. For example, if the bugzilla instance has some private bugs,
those bugs will be missing from 'query' output if you do not have an
active login.

If you are connecting to a bugzilla 5.0 or later instance, the best
option is to use bugzilla API keys. From the bugzilla web UI, log in,
navigate to Preferences->API Keys, and generate a key (it will be a long
string of characters and numbers). Then create a
~/.config/python-bugzilla/bugzillarc like this:

::

  $ cat ~/.config/python-bugzilla/bugzillarc

  [bugzilla.example.com]
  api_key=YOUR_API_KEY

Replace 'bugzilla.example.com' with your bugzilla host name, and
YOUR_API_KEY with the generated API Key from the Web UI.

Alternatively, you can use 'bugzilla login --api-key', which will ask
for the API key, and save it to bugzillarc for you.

For older bugzilla instances, you will need to cache a login cookie or
token with the "login" subcommand or the "--login" argument.

Additionally, the --no-cache-credentials option will tell the bugzilla
tool to *not* save or use any authentication cache, including the
bugzillarc file.


EXAMPLES
========

|   bugzilla query --bug_id 62037
|
|   bugzilla query --version 15 --component python-bugzilla
|
|   bugzilla login
|
|   bugzilla new -p Fedora -v rawhide -c python-bugzilla \\
|       --summary "python-bugzilla causes headaches" \\
|       --comment "python-bugzilla made my brain hurt when I used it."
|
|   bugzilla attach --file ~/Pictures/cam1.jpg --desc "me, in pain"
|   $BUGID
|
|   bugzilla attach --getall $BUGID
|
|   bugzilla modify --close NOTABUG --comment "Actually, you're
|   hungover." $BUGID


EXIT STATUS
===========

**bugzilla** normally returns 0 if the requested command was successful.
Otherwise, exit status is 1 if **bugzilla** is interrupted by the user
(or a login attempt fails), 2 if a socket error occurs (e.g. TCP
connection timeout), and 3 if the Bugzilla server throws an error.


BUGS
====

Please report any bugs as github issues at
https://github.com/python-bugzilla/python-bugzilla


SEE ALSO
========

https://bugzilla.readthedocs.io/en/latest/api/index.html
https://bugzilla.redhat.com/docs/en/html/api/Bugzilla/WebService/Bug.html
