import string

from shreducers import tokenizers
from shreducers.grammar import Grammar
from shreducers.tokenizers import EOF


class BetterArithmeticsG(Grammar):
    class t:
        IDENT = None
        PLUS_MINUS = '+-'
        MULTIPLY_DIVIDE = '*/'
        PARENS_OPEN = '('
        PARENS_CLOSE = ')'
        PRODUCT = ()

    @classmethod
    def get_default_tokenizer(cls):
        return tokenizers.create_shlex_tokenizer(with_eof=True, wordchars=string.digits + '.')

    @classmethod
    def get_rules(cls):
        return [
            ([cls.t.PRODUCT, cls.t.MULTIPLY_DIVIDE, cls.t.PRODUCT], cls.product_expr),
            ([cls.t.PRODUCT, cls.t.MULTIPLY_DIVIDE, cls.t.IDENT], cls.product_expr),
            ([cls.t.IDENT, cls.t.MULTIPLY_DIVIDE, cls.t.IDENT], cls.product_expr),
            ([cls.t.IDENT, cls.t.MULTIPLY_DIVIDE, cls.t.PRODUCT], cls.product_expr),

            # Plus/minus can only be applied when we've seen the entire string which means we've seen the EOF
            ([cls.t.IDENT, EOF], cls.product_at_eof),
            ([cls.t.IDENT, cls.t.PLUS_MINUS, cls.t.PRODUCT, EOF], cls.product_expr_at_eof),
            ([cls.t.PRODUCT, cls.t.PLUS_MINUS, cls.t.PRODUCT, EOF], cls.product_expr_at_eof),

            # Parentheses.
            ([cls.t.PARENS_OPEN, cls.t.PRODUCT, cls.t.PARENS_CLOSE], cls.remove_parens),

            # Closing parenthesis is very much like EOF. The next three rules are a copy of plus/minus rules above.
            ([cls.t.IDENT, cls.t.PARENS_CLOSE], cls.product_at_eof),
            ([cls.t.IDENT, cls.t.PLUS_MINUS, cls.t.PRODUCT, cls.t.PARENS_CLOSE], cls.product_expr_at_eof),
            ([cls.t.PRODUCT, cls.t.PLUS_MINUS, cls.t.PRODUCT, cls.t.PARENS_CLOSE], cls.product_expr_at_eof),
        ]

    @classmethod
    def product_expr(cls, types, (a, op, b)):
        return [cls.t.PRODUCT], [(op, a, b)]

    @classmethod
    def product_at_eof(cls, types, (a, eof)):
        return [cls.t.PRODUCT, types[1]], [a, eof]

    @classmethod
    def product_expr_at_eof(cls, types, (a, op, b, eof)):
        return [cls.t.PRODUCT, types[3]], [(op, a, b), eof]

    @classmethod
    def remove_parens(cls, types, (p1, x, p2)):
        return [[types[1]], [x]]
