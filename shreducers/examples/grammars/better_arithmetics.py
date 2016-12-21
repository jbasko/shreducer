import string

from shreducers import tokenizers
from shreducers.grammar import Grammar
from shreducers.tokenizers import EOF


class BetterArithmeticsG(Grammar):
    class t:
        IDENT = None
        PLUS_MINUS = '+-'
        MULTIPLY_DIVIDE = '*/'
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
        ]

    @classmethod
    def product_expr(cls, types, (a, op, b)):
        return [cls.t.PRODUCT], [(op, a, b)]

    @classmethod
    def product_at_eof(cls, types, (a, eof)):
        return [cls.t.PRODUCT, EOF], [a, eof]

    @classmethod
    def product_expr_at_eof(cls, types, (a, op, b, eof)):
        return [cls.t.PRODUCT, EOF], [(op, a, b), eof]
