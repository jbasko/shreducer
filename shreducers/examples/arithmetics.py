from shreducers.grammar import Grammar


class ArithmeticsG(Grammar):
    class t:
        IDENT = None
        PLUS_MINUS = '+', '-'
        PARENS_OPEN = '(',
        PARENS_CLOSE = ')',
        EXPR = ()

    @classmethod
    def get_rules(cls):
        return [
            # Basic addition and subtraction
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


_p = ArithmeticsG.parse
_s = ArithmeticsG.simple_parse


def test_simple_arithmetics():
    assert _p('2 + 3') == ([ArithmeticsG.t.EXPR], [('+', '2', '3')])
    assert _s('2 - 3') == ('-', '2', '3')
    assert _s('2 - 3 + 1') == ('+', ('-', '2', '3'), '1')


def test_basic_parentheses():
    assert _s('2 - (3 + 1)') == ('-', '2', ('+', '3', '1'))
    assert _s('(2 - 3) + 1') == ('+', ('-', '2', '3'), '1')

    assert _s('2 - (3 + (1 - 4))') == ('-', '2', ('+', '3', ('-', '1', '4')))
    assert _s('((2 - 3) + 1) - 4') == ('-', ('+', ('-', '2', '3'), '1'), '4')


def test_sign_before_identifier_and_expr():
    assert _s('-2 + 3') == ('+', ('-', '0', '2'), '3')
    assert _s('3 - -2') == ('-', '3', ('-', '0', '2'))

    assert _s('(-2) + 3') == ('+', ('-', '0', '2'), '3')
    assert _s('3 - (-2)') == ('-', '3', ('-', '0', '2'))

    assert _s('- (2 + 3)') == ('-', '0', ('+', '2', '3'))

    assert _s('- ( - (3 - 4))') == ('-', '0', ('-', '0', ('-', '3', '4')))
