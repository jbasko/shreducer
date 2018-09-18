import string

from shreducer import Grammar, tokenizers
from shreducer.tokenizers import EOF


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
        return tokenizers.create_shlex_tokenizer(
            with_bof=True,
            with_eof=True,
            wordchars=string.ascii_uppercase + string.ascii_lowercase + string.digits + '_.',
        )

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
    def begin_list(cls, types, xxx_todo_changeme):
        (a, comma) = xxx_todo_changeme
        return [cls.t.LIST, cls.t.COMMA], [('list', [a]), comma]

    @classmethod
    def append_to_list(cls, types, xxx_todo_changeme1):
        (head, comma, a) = xxx_todo_changeme1
        head[1].append(a)
        return [cls.t.LIST], [head]

    @classmethod
    def remove_list_parens(cls, types, xxx_todo_changeme2):
        (p1, a, p2) = xxx_todo_changeme2
        return [cls.t.DONE], [a]

    @classmethod
    def single_item_list(cls, types, xxx_todo_changeme3):
        (p1, a, p2) = xxx_todo_changeme3
        return [cls.t.DONE], [('list', [a])]

    @classmethod
    def done(cls, xxx_todo_changeme4, xxx_todo_changeme5):
        (a_type, ) = xxx_todo_changeme4
        (a, ) = xxx_todo_changeme5
        return [cls.t.DONE], [a]

    @classmethod
    def comparison(cls, types, xxx_todo_changeme6):
        (a, op, b) = xxx_todo_changeme6
        return [cls.t.EXPR], [(op, a, b)]

    @classmethod
    def inverted_negation(cls, xxx_todo_changeme7, xxx_todo_changeme8):
        (a_type, neg_type, op_type) = xxx_todo_changeme7
        (a, neg, op) = xxx_todo_changeme8
        return [neg_type, a_type, op_type], [neg, a, op]

    @classmethod
    def negation(cls, types, xxx_todo_changeme9):
        (neg, a) = xxx_todo_changeme9
        return [cls.t.EXPR], [(neg, a)]

    @classmethod
    def binary_logical_expr(cls, types, xxx_todo_changeme10):
        (expr1, op, expr2) = xxx_todo_changeme10
        return [cls.t.EXPR], [(op, expr1, expr2)]

    @classmethod
    def remove_expr_parens(cls, types, xxx_todo_changeme11):
        (p1, expr, p2) = xxx_todo_changeme11
        return [cls.t.EXPR], [expr]
