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
==============

``--help, -h``
^^^^^^^^^^^^^^

**Syntax:** ``-h``

show this help message and exit


``--bugzilla``
^^^^^^^^^^^^^^

**Syntax:** ``--bugzilla`` BUGZILLA

The bugzilla URL. Full API URLs are typically like:

|
| * https://bugzilla.example.com/xmlrpc.cgi    # XMLRPC API
| * https://bugzilla.example.com/rest/         # REST API
|

If a non-specific URL is passed, like 'bugzilla.redhat.com', **bugzilla**
will try to probe whether the expected XMLRPC or REST path is available,
preferring XMLRPC for backwards compatibility.

The default URL https://bugzilla.redhat.com


``--nosslverify``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--nosslverify``

Don't error on invalid bugzilla SSL certificate


``--cert``
^^^^^^^^^^

**Syntax:** ``--cert`` CERTFILE

client side certificate file needed by the webserver.


``--login``
^^^^^^^^^^^

**Syntax:** ``--login``

Run interactive "login" before performing the specified command.


``--username``
^^^^^^^^^^^^^^

**Syntax:** ``--username`` USERNAME

Log in with this username


``--password``
^^^^^^^^^^^^^^

**Syntax:** ``--password`` PASSWORD

Log in with this password


``--restrict-login``
^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--restrict-login``

The session (login token) will be restricted to the current IP
address.


``--ensure-logged-in``
^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--ensure-logged-in``

Raise an error if we aren't logged in to bugzilla. Consider using
this if you are depending on cached credentials, to ensure that when
they expire the tool errors, rather than subtly change output.


``--no-cache-credentials``
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--no-cache-credentials``

Don't save any bugzilla tokens to disk, and don't use any
pre-existing credentials.


``--tokenfile``
^^^^^^^^^^^^^^^

**Syntax:** ``--tokenfile`` TOKENFILE

token file to use for bugzilla authentication


``--verbose``
^^^^^^^^^^^^^

**Syntax:** ``--verbose``

give more info about what's going on


``--debug``
^^^^^^^^^^^

**Syntax:** ``--debug``

output bunches of debugging info


``--version``
^^^^^^^^^^^^^

**Syntax:** ``--version``

show program's version number and exit



Standard bugzilla options
=========================

These options are shared by some combination of the 'new', 'query', and
'modify' sub commands. Not every option works for each command though.


``-p, --product``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--product`` PRODUCT

Product name


``-v, --version``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--version`` VERSION

Product version


``-c, --component``
^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--component`` COMPONENT

Component name


``-s, --summary``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--summary`` SUMMARY

Bug summary


``-l, --comment``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--comment`` DESCRIPTION

Set initial bug comment/description


``--comment-tag``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--comment-tag`` TAG

Comment tag for the new comment


``--sub-component``
^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--sub-component`` SUB_COMPONENT

RHBZ sub component name


``-o, --os``
^^^^^^^^^^^^

**Syntax:** ``--os`` OS

Operating system


``--arch``
^^^^^^^^^^

**Syntax:** ``--arch`` ARCH

Arch this bug occurs on


``-x, --severity``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--severity`` SEVERITY

Bug severity


``-z, --priority``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--priority`` PRIORITY

Bug priority


``--alias``
^^^^^^^^^^^

**Syntax:** ``--alias`` ALIAS

Bug alias (name)


``-s, --status``
^^^^^^^^^^^^^^^^

**Syntax:** ``--status`` STATUS

Bug status (NEW, ASSIGNED, etc.)


``-u, --url``
^^^^^^^^^^^^^

**Syntax:** ``--url`` URL

URL for further bug info


``-m --target_milestone``
^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--target_milestone`` TARGET_MILESTONE

Target milestone


``--target_release``
^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--target_release`` TARGET_RELEASE

RHBZ Target release


``--blocked``
^^^^^^^^^^^^^

**Syntax:** ``...]``

Bug IDs that this bug blocks


``--dependson``
^^^^^^^^^^^^^^^

**Syntax:** ``...]``

Bug IDs that this bug depends on


``--keywords``
^^^^^^^^^^^^^^

**Syntax:** ``...]``

Bug keywords


``--groups``
^^^^^^^^^^^^

**Syntax:** ``...]``

Which user groups can view this bug


``--cc``
^^^^^^^^

**Syntax:** ``...]``

CC list


``-a, --assignee, --assigned_to``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--assigned_to`` ASSIGNED_TO

Bug assignee


``-q, --qa_contact``
^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--qa_contact`` QA_CONTACT

QA contact


``--flag``
^^^^^^^^^^

**Syntax:** ``--flag`` FLAG

Set or unset a flag. For example, to set a flag named devel_ack, do
--flag devel_ack+ Unset a flag with the 'X' value, like --flag
needinfoX


``--tags``
^^^^^^^^^^

**Syntax:** ``--tags`` TAG

Set (personal) tags field


``-w, --whiteboard``
^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--whiteboard`` WHITEBOARD

Whiteboard field


``--devel_whiteboard``
^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--devel_whiteboard`` DEVEL_WHITEBOARD

RHBZ devel whiteboard field


``--internal_whiteboard``
^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--internal_whiteboard`` INTERNAL_WHITEBOARD

RHBZ internal whiteboard field


``--qa_whiteboard``
^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--qa_whiteboard`` QA_WHITEBOARD

RHBZ QA whiteboard field


``-F, --fixed_in``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--fixed_in`` FIXED_IN

RHBZ 'Fixed in version' field


``--field``
^^^^^^^^^^^

**Syntax:** ``--field`` FIELD`` VALUE

Manually specify a bugzilla API field. FIELD is the raw name used
by the bugzilla instance. For example if your bugzilla instance has a
custom field cf_my_field, do: --field cf_my_field=VALUE



Output options
==============

These options are shared by several commands, for tweaking the text
output of the command results.


``-f, --full``
^^^^^^^^^^^^^^

**Syntax:** ``--full``

output detailed bug info


``-i, --ids``
^^^^^^^^^^^^^

**Syntax:** ``--ids``

output only bug IDs


``-e, --extra``
^^^^^^^^^^^^^^^

**Syntax:** ``--extra``

output additional bug information (keywords, Whiteboards, etc.)


``--oneline``
^^^^^^^^^^^^^

**Syntax:** ``--oneline``

one line summary of the bug (useful for scripts)


``--json``
^^^^^^^^^^

**Syntax:** ``--json``

output bug contents in JSON format


``--includefield``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--includefield``

Pass the field name to bugzilla include_fields list.
Only the fields passed to include_fields are returned
by the bugzilla server.
This can be specified multiple times.


``--extrafield``
^^^^^^^^^^^^^^^^

**Syntax:** ``--extrafield``

Pass the field name to bugzilla extra_fields list.
When used with --json this can be used to request
bugzilla to return values for non-default fields.
This can be specified multiple times.


``--excludefield``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--excludefield``

Pass the field name to bugzilla exclude_fields list.
When used with --json this can be used to request
bugzilla to not return values for a field.
This can be specified multiple times.


``--raw``
^^^^^^^^^

**Syntax:** ``--raw``

raw output of the bugzilla contents. This format is unstable and
difficult to parse. Please use the ``--json`` instead if you want
maximum output from the `bugzilla`


``--outputformat``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--outputformat`` OUTPUTFORMAT

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


``-b, --bug_id, --id``
^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--id`` ID

specify individual bugs by IDs, separated with commas


``-r, --reporter``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--reporter`` REPORTER

Email: search reporter email for given address


``--quicksearch``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--quicksearch`` QUICKSEARCH

Search using bugzilla's quicksearch functionality.


``--savedsearch``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--savedsearch`` SAVEDSEARCH

Name of a bugzilla saved search. If you don't own this saved search,
you must passed --savedsearch_sharer_id.


``--savedsearch-sharer-id``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--savedsearch-sharer-id`` SAVEDSEARCH_SHARER_ID

Owner ID of the --savedsearch. You can get this ID from the URL
bugzilla generates when running the saved search from the web UI.


``--from-url``
^^^^^^^^^^^^^^

**Syntax:** ``--from-url`` WEB_QUERY_URL

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


``-k, --close RESOLUTION``
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``RESOLUTION``

Close with the given resolution (WONTFIX, NOTABUG, etc.)


``-d, --dupeid``
^^^^^^^^^^^^^^^^

**Syntax:** ``--dupeid`` ORIGINAL

ID of original bug. Implies --close DUPLICATE


``--private``
^^^^^^^^^^^^^

**Syntax:** ``--private``

Mark new comment as private


``--reset-assignee``
^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--reset-assignee``

Reset assignee to component default


``--reset-qa-contact``
^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--reset-qa-contact``

Reset QA contact to component default


``--minor-update``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--minor-update``

Request bugzilla to not send any email about this change



‘new’ specific options
======================

``--private``
^^^^^^^^^^^^^

**Syntax:** ``--private``

Mark new comment as private



‘attach’ options
================

``-f, --file``
^^^^^^^^^^^^^^

**Syntax:** ``--file`` FILENAME

File to attach, or filename for data provided on stdin


``-d, --description``
^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--description`` DESCRIPTION

A short description of the file being attached


``-t, --type``
^^^^^^^^^^^^^^

**Syntax:** ``--type`` MIMETYPE

Mime-type for the file being attached


``-g, --get``
^^^^^^^^^^^^^

**Syntax:** ``--get`` ATTACHID

Download the attachment with the given ID


``--getall``
^^^^^^^^^^^^

**Syntax:** ``--getall`` BUGID

Download all attachments on the given bug


``--ignore-obsolete``
^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--ignore-obsolete``

Do not download attachments marked as obsolete.


``-l, --comment``
^^^^^^^^^^^^^^^^^

**Syntax:** ``--comment`` COMMENT

Add comment with attachment


‘info’ options
==============

``-p, --products``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--products``

Get a list of products


``-c, --components``
^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--components`` PRODUCT

List the components in the given product


``-o, --component_owners``
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--component_owners`` PRODUCT

List components (and their owners)


``-v, --versions``
^^^^^^^^^^^^^^^^^^

**Syntax:** ``--versions`` PRODUCT

List the versions for the given product


``--active-components``
^^^^^^^^^^^^^^^^^^^^^^^

**Syntax:** ``--active-components``

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

For older bugzilla instances, you will need to cache a login token
with the "login" subcommand or the "--login" argument.

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
https://bugzilla.redhat.com/docs/en/html/api/core/v1/bug.html
