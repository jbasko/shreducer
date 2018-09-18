from shreducer.grammar import Grammar


class FilterExpressionsG(Grammar):
    class t:
        IDENT = None
        BINARY_COMP_OP = 'eq', 'ne', 'gt', 'ge', 'lt', 'le', 'in'
        BINARY_LOGIC_OP = 'and', 'or'
        NOT = 'not',
        PARENS_OPEN = '('
        PARENS_CLOSE = ')'
        COMMA = ','

        EXPR = ()
        LIST = ()

    @classmethod
    def get_rules(cls):
        return [
            ([cls.t.IDENT, cls.t.BINARY_COMP_OP, cls.t.IDENT], cls.binary_expr),
            ([cls.t.EXPR, cls.t.BINARY_LOGIC_OP, cls.t.EXPR], cls.binary_expr),
            ([cls.t.PARENS_OPEN, cls.t.EXPR, cls.t.PARENS_CLOSE], cls.remove_parens),
            ([cls.t.NOT, cls.t.EXPR], cls.neg_expr),

            # Naive Lists
            ([cls.t.COMMA, cls.t.IDENT, cls.t.PARENS_CLOSE], cls.start_list_expr),
            ([cls.t.IDENT, cls.t.COMMA, cls.t.LIST], cls.continue_list_expr),
            ([cls.t.PARENS_OPEN, cls.t.LIST], cls.finish_list_expr),
            ([cls.t.IDENT, cls.t.BINARY_COMP_OP, cls.t.LIST], cls.binary_expr),
            ([cls.t.LIST, cls.t.BINARY_COMP_OP, cls.t.IDENT], cls.binary_expr),
            ([cls.t.LIST, cls.t.BINARY_COMP_OP, cls.t.LIST], cls.binary_expr),
        ]

    @classmethod
    def binary_expr(cls, types, xxx_todo_changeme):
        (a, op, b) = xxx_todo_changeme
        return [cls.t.EXPR], [(op, a, b)]

    @classmethod
    def remove_parens(cls, types, xxx_todo_changeme1):
        (p1, expr, p2) = xxx_todo_changeme1
        return [cls.t.EXPR], [expr]

    @classmethod
    def neg_expr(cls, types, xxx_todo_changeme2):
        (neg, a) = xxx_todo_changeme2
        return [cls.t.EXPR], [('not', a)]

    @classmethod
    def start_list_expr(cls, types, xxx_todo_changeme3):
        (comma, a, p) = xxx_todo_changeme3
        return [cls.t.COMMA, cls.t.LIST], [comma, ('list', [a])]

    @classmethod
    def continue_list_expr(cls, types, xxx_todo_changeme4):
        (a, comma, lst) = xxx_todo_changeme4
        lst[1].insert(0, a)
        return [cls.t.LIST], [lst]

    @classmethod
    def finish_list_expr(cls, types, xxx_todo_changeme5):
        (p, lst) = xxx_todo_changeme5
        return [cls.t.LIST], [lst]
