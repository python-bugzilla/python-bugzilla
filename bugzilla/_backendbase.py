# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.


class _BackendBase(object):
    """
    Backends are thin wrappers around the different bugzilla API paradigms
    (XMLRPC, REST). This base class defines the public API for the rest of
    the code, but this is all internal to the library.
    """
    def __init__(self, url, bugzillasession):
        self._url = url
        self._bugzillasession = bugzillasession

    #################
    # Internal APIs #
    #################

    def get_xmlrpc_proxy(self):
        """
        Provides the raw XMLRPC proxy to API users of Bugzilla._proxy
        """
        raise NotImplementedError()


    ######################
    # Bugzilla info APIs #
    ######################

    def bugzilla_version(self):
        """
        Fetch bugzilla version string
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bugzilla.html#version
        """
        raise NotImplementedError()

    def bugzilla_extensions(self):
        """
        Return info about Bugzilla extensions
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bugzilla.html#extensions
        """
        raise NotImplementedError()


    #######################
    # Bug attachment APIs #
    #######################

    def bug_attachment_get(self, attachment_ids, paramdict):
        """
        Fetch bug attachments IDs. One part of:
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/attachment.html#get-attachment
        """
        raise NotImplementedError()

    def bug_attachment_get_all(self, bug_ids, paramdict):
        """
        Fetch all bug attachments IDs. One part of
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/attachment.html#get-attachment
        """
        raise NotImplementedError()

    def bug_attachment_create(self, data, paramdict):
        """
        Create a bug attachment
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/attachment.html#create-attachment

        :param data: raw Bytes data of the attachment to attach. API will
            encode this correctly if you pass it in and 'data' is not in
            paramdict.
        """
        raise NotImplementedError()

    def bug_attachment_update(self, paramdict):
        """
        Update a bug attachment
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/attachment.html#update-attachment
        """
        raise NotImplementedError()


    ############
    # bug APIs #
    ############

    def bug_comments(self, paramdict):
        """
        Fetch bug comments
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/comment.html#get-comments
        """
        raise NotImplementedError()

    def bug_create(self, paramdict):
        """
        Create a new bug
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#create-bug
        """
        raise NotImplementedError()

    def bug_fields(self, paramdict):
        """
        Query available bug field values
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/field.html#fields
        """
        raise NotImplementedError()

    def bug_get(self, paramdict):
        """
        Lookup bug data by ID
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#get-bug
        """
        raise NotImplementedError()

    def bug_history(self, paramdict):
        """
        Lookup bug history
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#bug-history
        """
        raise NotImplementedError()

    def bug_legal_values(self, paramdict):
        """
        Old style fields querying
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/field.html#legal-values
        """
        raise NotImplementedError()

    def bug_search(self, paramdict):
        """
        Search/query bugs
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#search-bugs
        """
        raise NotImplementedError()

    def bug_update(self, paramdict):
        """
        Update bugs
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#update-bug
        """
        raise NotImplementedError()

    def bug_update_tags(self, paramdict):
        """
        Update bug tags
        https://www.bugzilla.org/docs/4.4/en/html/api/Bugzilla/WebService/Bug.html#update_tags
        """
        raise NotImplementedError()


    ##################
    # Component APIs #
    ##################

    def component_create(self, paramdict):
        """
        Create component
        https://bugzilla.readthedocs.io/en/latest/api/core/v1/component.html#create-component
        """
        raise NotImplementedError()

    def component_update(self, paramdict):
        """
        Update component
        https://bugzilla.readthedocs.io/en/latest/api/core/v1/component.html#update-component
        """
        raise NotImplementedError()


    ###############################
    # ExternalBugs extension APIs #
    ###############################

    def externalbugs_add(self, paramdict):
        """
        https://bugzilla.redhat.com/docs/en/html/integrating/api/Bugzilla/Extension/ExternalBugs/WebService.html#add-external-bug
        """
        raise NotImplementedError()

    def externalbugs_update(self, paramdict):
        """
        https://bugzilla.redhat.com/docs/en/html/integrating/api/Bugzilla/Extension/ExternalBugs/WebService.html#update-external-bug
        """
        raise NotImplementedError()

    def externalbugs_remove(self, paramdict):
        """
        https://bugzilla.redhat.com/docs/en/html/integrating/api/Bugzilla/Extension/ExternalBugs/WebService.html#remove-external-bug
        """
        raise NotImplementedError()


    ################
    # Product APIs #
    ################

    def product_get(self, paramdict):
        """
        Fetch product details
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/product.html#get-product
        """
        raise NotImplementedError()

    def product_get_accessible(self):
        """
        List accessible products
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/product.html#list-products
        """
        raise NotImplementedError()

    def product_get_enterable(self):
        """
        List enterable products
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/product.html#list-products
        """
        raise NotImplementedError()

    def product_get_selectable(self):
        """
        List selectable products
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/product.html#list-products
        """
        raise NotImplementedError()


    #############
    # User APIs #
    #############

    def user_create(self, paramdict):
        """
        Create user
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/user.html#create-user
        """
        raise NotImplementedError()

    def user_get(self, paramdict):
        """
        Get user info
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/user.html#get-user
        """
        raise NotImplementedError()

    def user_login(self, paramdict):
        """
        Log in to bugzilla
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/user.html#login
        """
        raise NotImplementedError()

    def user_logout(self):
        """
        Log out of bugzilla
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/user.html#logout
        """
        raise NotImplementedError()

    def user_update(self, paramdict):
        """
        Update user
        http://bugzilla.readthedocs.io/en/latest/api/core/v1/user.html#update-user
        """
        raise NotImplementedError()
