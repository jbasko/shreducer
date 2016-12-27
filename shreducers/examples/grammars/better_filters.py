from shreducers import tokenizers
from shreducers.grammar import Grammar
from shreducers.tokenizers import EOF


class BetterFiltersG(Grammar):
    class t:
        ID = None
        COMMA = ','
        PARENS_OPEN = '('
        PARENS_CLOSE = ')'

        COMPARISON_OP = 'gt', 'ge', 'lt', 'le', 'eq', 'ne', 'in'
        AND_OR = 'and', 'or'
        NOT = 'not',

        LIST = ()

        # An ID or LIST that is completed and cannot be modified anymore
        # DONE must have all the rules that ID has.
        DONE = ()

        EXPR = ()

    @classmethod
    def get_default_tokenizer(cls):
        return tokenizers.create_shlex_tokenizer(with_bof=True, with_eof=True)

    @classmethod
    def get_rules(cls):
        yield ([cls.t.ID, cls.t.COMMA], cls.begin_list)
        yield ([cls.t.DONE, cls.t.COMMA], cls.begin_list)
        yield ([cls.t.LIST, cls.t.COMMA, cls.t.ID], cls.append_to_list)
        yield ([cls.t.LIST, cls.t.COMMA, cls.t.DONE], cls.append_to_list)
        yield ([cls.t.PARENS_OPEN, cls.t.DONE, cls.t.PARENS_CLOSE], cls.remove_list_parens)
        yield ([cls.t.PARENS_OPEN, cls.t.ID, cls.t.PARENS_CLOSE], cls.single_item_list)

        for lookahead in (cls.t.AND_OR, cls.t.PARENS_CLOSE, EOF):
            yield ([cls.t.LIST], lookahead, cls.done)
            yield ([cls.t.ID], lookahead, cls.done)

        for lookahead in (cls.t.AND_OR, cls.t.PARENS_CLOSE, EOF):
            yield ([cls.t.ID, cls.t.COMPARISON_OP, cls.t.DONE], lookahead, cls.comparison)
            yield ([cls.t.LIST, cls.t.COMPARISON_OP, cls.t.DONE], lookahead, cls.comparison)
            yield ([cls.t.DONE, cls.t.COMPARISON_OP, cls.t.DONE], lookahead, cls.comparison)

        yield ([cls.t.ID, cls.t.NOT, cls.t.COMPARISON_OP], cls.inverted_negation)
        yield ([cls.t.LIST, cls.t.NOT, cls.t.COMPARISON_OP], cls.inverted_negation)
        yield ([cls.t.DONE, cls.t.NOT, cls.t.COMPARISON_OP], cls.inverted_negation)

        yield ([cls.t.NOT, cls.t.EXPR], cls.negation)

        yield ([cls.t.EXPR, cls.t.AND_OR, cls.t.EXPR], cls.binary_logical_expr)

        yield ([cls.t.PARENS_OPEN, cls.t.EXPR, cls.t.PARENS_CLOSE], cls.remove_expr_parens)

    @classmethod
    def begin_list(cls, types, (a, comma)):
        return [cls.t.LIST, cls.t.COMMA], [('list', [a]), comma]

    @classmethod
    def append_to_list(cls, types, (head, comma, a)):
        head[1].append(a)
        return [cls.t.LIST], [head]

    @classmethod
    def remove_list_parens(cls, types, (p1, a, p2)):
        return [cls.t.DONE], [a]

    @classmethod
    def single_item_list(cls, types, (p1, a, p2)):
        return [cls.t.DONE], [('list', [a])]

    @classmethod
    def done(cls, (a_type, ), (a, )):
        return [cls.t.DONE], [a]

    @classmethod
    def comparison(cls, types, (a, op, b)):
        return [cls.t.EXPR], [(op, a, b)]

    @classmethod
    def inverted_negation(cls, (a_type, neg_type, op_type), (a, neg, op)):
        return [neg_type, a_type, op_type], [neg, a, op]

    @classmethod
    def negation(cls, types, (neg, a)):
        return [cls.t.EXPR], [(neg, a)]

    @classmethod
    def binary_logical_expr(cls, types, (expr1, op, expr2)):
        return [cls.t.EXPR], [(op, expr1, expr2)]

    @classmethod
    def remove_expr_parens(cls, types, (p1, expr, p2)):
        return [cls.t.EXPR], [expr]
