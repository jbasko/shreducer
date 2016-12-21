from shreducers.grammar import Grammar


class FilterExpressionsG(Grammar):
    class t:
        IDENT = None
        BINARY_COMP_OP = 'eq', 'ne', 'gt', 'ge', 'lt', 'le'
        BINARY_LOGIC_OP = 'and', 'or'
        PARENS_OPEN = '('
        PARENS_CLOSE = ')'
        NOT = 'not',

        EXPR = ()

    @classmethod
    def get_rules(cls):
        return [
            ([cls.t.IDENT, cls.t.BINARY_COMP_OP, cls.t.IDENT], cls.binary_expr),
            ([cls.t.EXPR, cls.t.BINARY_LOGIC_OP, cls.t.EXPR], cls.binary_expr),
            ([cls.t.PARENS_OPEN, cls.t.EXPR, cls.t.PARENS_CLOSE], cls.remove_parens),

            ([cls.t.NOT, cls.t.EXPR], cls.neg_expr),
        ]

    @classmethod
    def binary_expr(cls, types, (a, op, b)):
        return [cls.t.EXPR], [(op, a, b)]

    @classmethod
    def remove_parens(cls, types, (p1, expr, p2)):
        return [cls.t.EXPR], [expr]

    @classmethod
    def neg_expr(cls, types, (neg, a)):
        return [cls.t.EXPR], [('not', a)]
