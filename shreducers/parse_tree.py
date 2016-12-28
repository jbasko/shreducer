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
    __slots__ = ('op', 'a', 'b', 'x')

    def __init__(self, *args, **kwargs):
        self.op = None
        self.a = None
        self.b = None
        self.x = PtNodeExtras()

        if args:
            if len(args) == 1:
                args = args[0]

            for i, k in enumerate(self.__slots__):
                if len(args) > i:
                    setattr(self, k, args[i])

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @property
    def operands(self):
        if self.b is None:
            return self.a,
        else:
            return self.a, self.b

    def to_tuple(self):
        return (self.op,) + tuple(ab.to_tuple() if isinstance(ab, PtNode) else ab for ab in self.operands)

    def __repr__(self):
        return '<{} op={}, a={}, b={}, x={}>'.format(self.__class__.__name__, self.op, self.a, self.b, self.x)


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

    def __new__(cls, *args):
        instance = super(ParseTreeProcessor, cls).__new__(cls, *args)
        for k, v in cls.__dict__.iteritems():
            if v and callable(v) and hasattr(v, 'delegate_of'):
                for d in v.delegate_of:
                    # Must assign the bounded method of instance, not that of the class
                    setattr(instance, d, getattr(instance, k))
        return instance

    def process(self, node):
        if isinstance(node, tuple):
            node = PtNode(node)
        if isinstance(node, PtNode):
            node.a = self.process(node.a)
            if node.b is not None:
                node.b = self.process(node.b)
            return self.do_process(node)
        else:
            return self.process_primitive(node)

    def do_process(self, node):
        processor_name = 'process_{}'.format(node.op)
        if hasattr(self, processor_name):
            return getattr(self, processor_name)(node)
        else:
            return self.process_unrecognised(node)

    def process_primitive(self, primitive):
        return primitive

    def process_unrecognised(self, node):
        return node


class ParseTreeMultiProcessor(ParseTreeProcessor):
    """
    Represents a chain of processors that need to be applied on each node
    one after another.

    This class should not be extended as that would complicate thinking about
    how it works.
    """

    def __init__(self, *processors):
        self._processors = processors
        if self.__class__.__name__ != ParseTreeMultiProcessor.__name__:
            raise RuntimeError('Attempting to extend {}'.format(ParseTreeMultiProcessor.__name__))

    def _process_with_all(self, method_name, node):
        for p in self._processors or ():
            node = getattr(p, method_name)(node)
        return node

    def process(self, node):
        if isinstance(node, tuple):
            node = PtNode(node)
        if isinstance(node, PtNode):
            node.a = self._process_with_all(self.process.__name__, node.a)
            if node.b is not None:
                node.b = self._process_with_all(self.process.__name__, node.b)
            return self._process_with_all(self.do_process.__name__, node)
        else:
            return self._process_with_all(self.process_primitive.__name__, node)

    def do_process(self, node):
        raise RuntimeError('Do not call this')

    def process_primitive(self, primitive):
        raise RuntimeError('Do not call this')

    def process_unrecognised(self, node):
        raise RuntimeError('Do not call this')

