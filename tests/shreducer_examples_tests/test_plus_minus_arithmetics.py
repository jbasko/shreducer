from shreducer_examples.grammars.plus_minus_arithmetics import PlusMinusArithmeticsG

_p = PlusMinusArithmeticsG.parse
_s = PlusMinusArithmeticsG.simple_parse


def test_simple_arithmetics():
    assert _p('2 + 3') == ([PlusMinusArithmeticsG.t.EXPR], [('+', '2', '3')])
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

    assert _s('1 - 2 - (3 - 4)')


def test_dots_dont_break_up_identifiers():
    assert _s('22.33 + 0.7') == ('+', '22.33', '0.7')
