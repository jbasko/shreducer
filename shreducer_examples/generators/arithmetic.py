import operator

from shreducer.generators import Generator


class ArithmeticGenerator(Generator):
    """
    Evaluates the parse tree produced by arithmetic parsers.
    """

    ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }

    def run(cls, tree):
        if isinstance(tree, tuple):
            if len(tree) == 3:
                operator_name = tree[0]

                if operator_name not in cls.ops:
                    raise ValueError('Unsupported operator: {}'.format(operator_name))

                operator = cls.ops[operator_name]
                operand1 = cls.run(tree[1])
                operand2 = cls.run(tree[2])
                return operator(operand1, operand2)

            else:
                raise ValueError('Unexpected syntax tree element: {}'.format(tree))

        elif isinstance(tree, str):
            float_val = float(tree)
            if '.' not in tree:
                return int(tree)
            else:
                return float_val

        else:
            raise TypeError('Parse tree element of unexpected type: {!r}'.format(tree))
