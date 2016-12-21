import string

from shreducers.grammar import Grammar
from shreducers.tokenizers import create_shlex_tokenizer


class PlusMinusArithmeticsG(Grammar):
    """
    Simple arithmetic expression parser that doesn't deal with multiplication and division
    because they have precedence over addition and subtraction which complicates the grammar.
    """

    class t:
        IDENT = None
        PLUS_MINUS = '+-'
        PARENS_OPEN = '('
        PARENS_CLOSE = ')'
        EXPR = ()

    @classmethod
    def get_default_tokenizer(cls):
        return create_shlex_tokenizer(wordchars=string.digits + '.')

    @classmethod
    def get_rules(cls):
        return [
            # Basic addition and subtraction
            ([cls.t.EXPR, cls.t.PLUS_MINUS, cls.t.EXPR], cls.binary_expr),
            ([cls.t.IDENT, cls.t.PLUS_MINUS, cls.t.IDENT], cls.binary_expr),
            ([cls.t.EXPR, cls.t.PLUS_MINUS, cls.t.IDENT], cls.binary_expr),
            ([cls.t.IDENT, cls.t.PLUS_MINUS, cls.t.EXPR], cls.binary_expr),

            # Parentheses
            ([cls.t.PARENS_OPEN, cls.t.EXPR, cls.t.PARENS_CLOSE], cls.remove_parens),

            # Minus signs: -1, -(2 + 3)
            ([cls.t.PLUS_MINUS, cls.t.IDENT], cls.negation),
            ([cls.t.PLUS_MINUS, cls.t.EXPR], cls.negation),
        ]

    @classmethod
    def binary_expr(cls, types, (a, op, b)):
        return [cls.t.EXPR], [(op, a, b)]

    @classmethod
    def remove_parens(cls, (t1, x_type, t2), (p1, x_value, p2)):
        return [x_type], [x_value]

    @classmethod
    def negation(cls, types, (_, a)):
        # -1 is effectively "0 - 1"
        return [cls.t.EXPR], [('-', '0', a)]
