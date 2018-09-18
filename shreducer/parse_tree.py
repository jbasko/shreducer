class PtNodeExtras(dict):
    """
    A dictionary with attribute-like access.
    Handy while processing parse tree and you
    need to store extra information about tree node
    as you discover it.
    """

    def __missing__(self, key):
        self[key] = None
        return self[key]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


class PtNode(object):
    """
    Represents a node in parse tree.
    """
    def __init__(self, *args, **kwargs):
        self._op = None
        self._a = None
        self._b = None
        self._x = PtNodeExtras()

        if args:
            if len(args) == 1:
                args = args[0]

            for i, k in enumerate(('op', 'a', 'b', 'x')):
                if len(args) > i:
                    setattr(self, '_' + k, args[i])

        for k, v in kwargs.items():
            setattr(self, '_' + k, v)

    @property
    def a(self):
        if isinstance(self._a, tuple):
            self._a = PtNode(self._a)
        return self._a

    @a.setter
    def a(self, value):
        self._a = value

    @property
    def b(self):
        if isinstance(self._b, tuple):
            self._b = PtNode(self._b)
        return self._b

    @b.setter
    def b(self, value):
        self._b = value

    @property
    def op(self):
        return self._op

    @op.setter
    def op(self, value):
        self._op = value

    @property
    def x(self):
        return self._x

    @property
    def operands(self):
        if self.b is None:
            return self.a,
        else:
            return self.a, self.b

    def mark_operands(self, **marks):
        if self.a is not None and isinstance(self.a, PtNode):
            self.a.x.update(marks)
        if self.b is not None and isinstance(self.b, PtNode):
            self.b.x.update(marks)

    def to_tuple(self):
        return (self.op,) + tuple(ab.to_tuple() if isinstance(ab, PtNode) else ab for ab in self.operands)

    def __repr__(self):
        return '<{} op={}, a={}, b={}, x={}>'.format(self.__class__.__name__, self.op, self.a, self.b, self.x)

    @property
    def is_leaf(self):
        """
        Returns True if there is no tree of nodes below this node.

        Note that ('eq', 'a', 'b') is a leaf node.
        Primitive operands aren't wrapped in PtNodes, so this would never be called for 'a' or 'b'.
        """
        return not isinstance(self.a, PtNode) and not isinstance(self.b, PtNode)


class PtNodeNotRecognised(Exception):
    """
    The exception that strict processors can choose to throw when encountering
    a node not handled by any process method.
    """
    def __init__(self, node):
        super(PtNodeNotRecognised, self).__init__('{!r}'.format(node))
        self.node = node


class ParseTreeProcessor(object):
    """
    Generic parse tree processor that other processors can extend
    and just implement custom node processors in methods called
    `process_<op>` where `<op>` is name of operator.

    To process primitive nodes implement `process_primitive`.

    To catch all non-primitive nodes, implement `process_unrecognised`.

    Make sure each processor does one thing and does it well.
    If you have a few different things to do before a parse tree can be compiled,
    you may want to use ParseTreeMultiProcessor which is a chain of processors.
    """

    strict = False
    pre_order = False

    class delegate_of(object):
        """
        Decorator to allow writing one method that does the job of many.
        This is handy when you want to process a number of operators with the
        same code.
        """
        def __init__(self, *method_names):
            self.delegate_of = method_names

        def __call__(self, func):
            func.delegate_of = self.delegate_of
            return func

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        for k, v in cls.__dict__.items():
            if v and callable(v) and hasattr(v, 'delegate_of'):
                for d in v.delegate_of:
                    # Must assign the bounded method of instance, not that of the class
                    setattr(instance, d, getattr(instance, k))
        return instance

    def __init__(self, strict=None, pre_order=None):
        """
        If `strict` is True, the processor will raise PtNodeNotRecognised when a node is not picked up by
        any process_<op>(node) handler.

        If `pre_order` is True, the node will be processed before processing its operands node.a and node.b.

        By default, the processor traverses parse tree in post-order which means that all process_<op>
        handlers work with node whose operands are already processed by this processor.
        """
        self._strict = strict if strict is not None else self.strict
        self._pre_order = pre_order if pre_order is not None else self.pre_order

    def process(self, node):
        if isinstance(node, tuple):
            node = PtNode(node)

        if not isinstance(node, PtNode):
            return self.process_primitive(node)

        if self._pre_order:
            node = self.do_process(node)

        node.a = self.process(node.a)
        if node.b is not None:
            node.b = self.process(node.b)

        if not self._pre_order:
            node = self.do_process(node)

        return node

    def do_process(self, node):
        processor_name = 'process_{}'.format(node.op)
        if hasattr(self, processor_name):
            return getattr(self, processor_name)(node)
        else:
            return self.process_unrecognised(node)

    def process_primitive(self, primitive):
        return primitive

    def process_unrecognised(self, node):
        """
        Handles nodes that aren't picked up by any concrete process_<op> methods because the processor
        doesn't have them.

        When overriding this method, do not call super() and do not set node.x.recognised to False as below
        because that would break strict parsing in multi processor which relies on that marker in detecting
        that no processor recognised this node.
        """
        if self._strict:
            raise PtNodeNotRecognised(node=node)
        else:
            node.x.recognised = False
            return node


class ParseTreeMultiProcessor(ParseTreeProcessor):
    """
    Represents a chain of processors that need to be applied on each node
    one after another.

    This class should not be extended as that would complicate thinking about
    how it works.
    """

    def __init__(self, *processors):
        if self.__class__.__name__ != ParseTreeMultiProcessor.__name__:
            raise RuntimeError('Attempting to extend {}'.format(ParseTreeMultiProcessor.__name__))

        self._all_slots = []
        self._current_slot_index = None

        if processors:
            self.slot(*processors)

    def _create_process_unrecognised_from_function(self, func):
        def process_unrecognised(inst, node):
            return func(node)
        return process_unrecognised

    def _validate_slot(self, slot):
        pre_order = None
        for i, p in enumerate(slot['processors']):
            if not isinstance(p, ParseTreeProcessor) and callable(p):
                # Create processor on the fly based on the function passed
                p_cls = type(p.__name__, (ParseTreeProcessor,), {
                    'pre_order': '_pre_' in p.__name__,
                    'process_unrecognised': self._create_process_unrecognised_from_function(p),
                })
                p = p_cls()
                slot['processors'][i] = p

            if pre_order is None:
                pre_order = p._pre_order
            if pre_order != p._pre_order:
                raise RuntimeError('Processors of incompatible pre/post order traversals in one slot')
        slot['pre_order'] = pre_order

    def slot(self, *processors):
        """
        Registers a collection of processors that will be run "in parallel" after
        any previously registered slots have processed the entire tree.
        """
        self._all_slots.append({
            'strict': False,
            'processors': list(processors),
            'pre_order': None,
        })
        self._validate_slot(self._all_slots[-1])
        return self

    def strict_slot(self, *processors):
        """
        Same as slot() with only exception being that every node is required to be recognised
        by at least one of the processors.
        """
        self._all_slots.append({
            'strict': True,
            'processors': list(processors),
            'pre_order': None,
        })
        self._validate_slot(self._all_slots[-1])
        return self

    @property
    def _current_slot(self):
        """
        Returns a list of processors that can be applied in "parallel" which is
        in the same -- current -- traversal of the tree.
        """
        return self._all_slots[self._current_slot_index]

    def _process_in_current_slot(self, method_name, node):
        """
        Returns `node` after it has been passed through `method_name` method of all processors in the current slot.
        """
        recognised = False
        for p in self._current_slot['processors']:
            if not isinstance(node, PtNode):
                # Primitives are considered recognised
                recognised = True
                node = getattr(p, self.process_primitive.__name__)(node)
            else:
                # If node reaches the default process_unrecognised(), node.x.recognised will be reset to False
                # and we'll know that this processor hasn't recognised it.
                node.x.recognised = True
                node = getattr(p, method_name)(node)
                recognised = recognised or node.x.recognised

        if self._current_slot['strict'] and not recognised:
            raise PtNodeNotRecognised(node=node)

        return node

    def process(self, node):
        """
        This method is called only once with the root node.
        """

        if isinstance(node, tuple):
            node = PtNode(node)

        if not isinstance(node, PtNode):
            raise RuntimeError('Did not expect here anything but PtNode instances, got {} instead'.format(node))

        assert node.x.is_root is None
        node.x.is_root = True
        node.mark_operands(is_root=False)

        self._current_slot_index = 0
        while self._current_slot_index < len(self._all_slots):
            if self._current_slot['pre_order']:
                node = self._process_in_current_slot(self.do_process.__name__, node)

            node.a = self._process_in_current_slot(self.process.__name__, node.a)
            if node.b is not None:
                node.b = self._process_in_current_slot(self.process.__name__, node.b)

            if not self._current_slot['pre_order']:
                node = self._process_in_current_slot(self.do_process.__name__, node)

            self._current_slot_index += 1

        return node

    def do_process(self, node):
        raise RuntimeError('Do not call this')

    def process_primitive(self, primitive):
        raise RuntimeError('Do not call this')

    def process_unrecognised(self, node):
        raise RuntimeError('Do not call this')


class ParseTreeInspector(ParseTreeProcessor):
    pre_order = True
    strict = True

    def process_unrecognised(self, node):
        node.x.print_indent = node.x.print_indent or 0
        node.mark_operands(print_indent=node.x.print_indent + 2)
        if node.is_leaf:
            print('{:50} {}'.format((' ' * node.x.print_indent) + node.op + ' ' + str(node.operands), node.x))
        else:
            print('{:50} {}'.format((' ' * node.x.print_indent) + node.op, node.x))
        return node
