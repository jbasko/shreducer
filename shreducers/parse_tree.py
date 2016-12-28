class ParseTreeExtras(dict):
    def __missing__(self, key):
        self[key] = None
        return self[key]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


class ParseTree(object):
    __slots__ = ('op', 'a', 'b', 'x')

    def __init__(self, *args, **kwargs):
        self.op = None
        self.a = None
        self.b = None
        self.x = ParseTreeExtras()

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
        return (self.op,) + tuple(ab.to_tuple() if isinstance(ab, ParseTree) else ab for ab in self.operands)
