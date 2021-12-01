# Copyright (c) Django Software Foundation and individual contributors.
# License: BSD-3-Clause
#
# both classes are extracted from:
# https://github.com/django/django/blob/f0480ddd2d3cb04b784cf7ea697f792b45c689cc/django/utils/tree.py
# https://github.com/django/django/blob/f0480ddd2d3cb04b784cf7ea697f792b45c689cc/django/db/models/query_utils.py

import copy


class Node:
    """
    A single internal node in the tree graph. A Node should be viewed as a
    connection (the root) with the children being either leaf nodes or other
    Node instances.
    """
    # Standard connector type. Clients usually won't use this at all and
    # subclasses will usually override the value.
    default = 'DEFAULT'

    def __init__(self, children=None, connector=None, negated=False):
        """Construct a new Node. If no connector is given, use the default."""
        self.children = children[:] if children else []
        self.connector = connector or self.default
        self.negated = negated

    # Required because django.db.models.query_utils.Q. Q. __init__() is
    # problematic, but it is a natural Node subclass in all other respects.
    @classmethod
    def _new_instance(cls, children=None, connector=None, negated=False):
        """
        Create a new instance of this class when new Nodes (or subclasses) are
        needed in the internal code in this class. Normally, it just shadows
        __init__(). However, subclasses with an __init__ signature that aren't
        an extension of Node.__init__ might need to implement this method to
        allow a Node to create a new instance of them (if they have any extra
        setting up to do).
        """
        obj = Node(children, connector, negated)
        obj.__class__ = cls
        return obj

    def __str__(self):
        template = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return template % (self.connector,
                           ', '.join(str(c) for c in self.children))

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __deepcopy__(self, memodict):
        obj = Node(connector=self.connector, negated=self.negated)
        # pylint: disable=invalid-class-object
        obj.__class__ = self.__class__
        obj.children = copy.deepcopy(self.children, memodict)
        return obj

    def __len__(self):
        """Return the number of children this node has."""
        return len(self.children)

    def __bool__(self):
        """Return whether or not this node has children."""
        return bool(self.children)

    def __contains__(self, other):
        """Return True if 'other' is a direct child of this instance."""
        return other in self.children

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.connector == other.connector and
            self.negated == other.negated and
            self.children == other.children
        )

    def add(self, data, conn_type):
        """
        Combine this tree and the data represented by data using the
        connector conn_type. The combine is done by squashing the node other
        away if possible.
        This tree (self) will never be pushed to a child node of the
        combined tree, nor will the connector or negated properties change.
        Return a node which can be used in place of data regardless if the
        node other got squashed or not.
        """
        if self.connector != conn_type:
            obj = self._new_instance(self.children, self.connector,
                                     self.negated)
            self.connector = conn_type
            self.children = [obj, data]
            return data
        elif (
            isinstance(data, Node) and
            not data.negated and
            (data.connector == conn_type or len(data) == 1)
        ):
            # We can squash the other node's children directly into this node.
            # We are just doing (AB)(CD) == (ABCD) here, with the addition that
            # if the length of the other node is 1 the connector doesn't
            # matter. However, for the len(self) == 1 case we don't want to do
            # the squashing, as it would alter self.connector.
            self.children.extend(data.children)
            return self
        else:
            # We could use perhaps additional logic here to see if some
            # children could be used for pushdown here.
            self.children.append(data)
            return data

    def negate(self):
        """Negate the sense of the root connector."""
        self.negated = not self.negated


class Q(Node):
    """
    Encapsulate filters as objects that can then be combined logically (using
    `&` and `|`).
    """
    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND
    conditional = True

    def __init__(self, *args, _connector=None, _negated=False, **kwargs):
        super().__init__(children=[*args, *sorted(kwargs.items())],
                         connector=_connector, negated=_negated)

    def _combine(self, other, conn):
        if not(isinstance(other, Q) or
               getattr(other, 'conditional', False) is True):
            raise TypeError(other)

        if not self:
            return other.copy() if hasattr(other, 'copy') else copy.copy(other)
        elif isinstance(other, Q) and not other:
            # pylint: disable=unused-variable
            _, args, kwargs = self.deconstruct()
            return type(self)(*args, **kwargs)

        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        # note: the following lines differs from upstream Django
        # ~OR(...) in Django gives (NOT (AND: (OR: (...)))) instead of
        # (NOT (OR: (...))). This is logical equivalent, but not desired
        # in this case
        # obj.add(self, self.AND)
        obj.connector = self.connector
        obj.add(self, self.connector)
        obj.negate()
        return obj

    def deconstruct(self):
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        if path.startswith('django.db.models.query_utils'):
            path = path.replace('django.db.models.query_utils',
                                'django.db.models')
        args = tuple(self.children)
        kwargs = {}
        if self.connector != self.default:
            kwargs['_connector'] = self.connector
        if self.negated:
            kwargs['_negated'] = True
        return path, args, kwargs
