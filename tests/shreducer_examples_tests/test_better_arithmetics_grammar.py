from shreducer_examples.grammars.better_arithmetics import BetterArithmeticsG

_p = BetterArithmeticsG.parse
_s = BetterArithmeticsG.simple_parse


def test_simple_multiplication_and_division():
    assert _s('2 * 3') == ('*', '2', '3')
    assert _s('2 / 3') == ('/', '2', '3')

    assert _s('2 * 3 * 4') == ('*', ('*', '2', '3'), '4')
    assert _s('2 / 3 / 4 / 5') == ('/', ('/', ('/', '2', '3'), '4'), '5')


def test_multiplication_precedes_addition():
    assert _s('2 + 3 * 4') == ('+', '2', ('*', '3', '4'))
    assert _s('2 * 3 + 4') == ('+', ('*', '2', '3'), '4')
    assert _s('2 + 3 * 4 + 5') == ('+', '2', ('+', ('*', '3', '4'), '5'))
    assert _s('2 * 3 + 4 * 5') == ('+', ('*', '2', '3'), ('*', '4', '5'))


def test_dots_dont_break_up_identifiers():
    assert _s('2.3 * 44.55') == ('*', '2.3', '44.55')


def test_parentheses():
    assert _s('(2 + 3)') == ('+', '2', '3')
    assert _s('(2 * 3)') == ('*', '2', '3')
    assert _s('(2 + 3) * 4') == ('*', ('+', '2', '3'), '4')
    assert _s('(2 + 3) * 4 - 5') == ('-', ('*', ('+', '2', '3'), '4'), '5')
    assert _s('2 * (3 + 4)') == ('*', '2', ('+', '3', '4'))
    assert _s('2 + (3 * 4) + 5') == ('+', '2', ('+', ('*', '3', '4'), '5'))
    assert _s('2 + (3 + 4 * 5)') == ('+', '2', ('+', '3', ('*', '4', '5')))
    assert _s('2 + (3 * 4 + 5)') == ('+', '2', ('+', ('*', '3', '4'), '5'))


def test_negation():
    assert _s('-2') == '-2'

    assert _s('-2 + 3') == ('+', '-2', '3')
    assert _s('2 + (-3)') == ('+', '2', '-3')

    assert _s('(-2 + 3)') == ('+', '-2', '3')

    assert _s('(-2) - (-3)') == ('-', '-2', '-3')
    assert _s('(-2) * (-3)') == ('*', '-2', '-3')

    assert _s('-2 * 3') == ('*', '-2', '3')
    assert _s('(-2 * 3)') == ('*', '-2', '3')

    assert _s('-2 * 3 + 4') == ('+', ('*', '-2', '3'), '4')

    assert _s('-2 + (-3 * 4)') == ('+', '-2', ('*', '-3', '4'))

    assert _s('-(2)') == ('-', '0', '2')
    assert _s('-(2) * 3') == ('*', ('-', '0', '2'), '3')
    assert _s('-(2 - 3) * 4') == ('*', ('-', '0', ('-', '2', '3')), '4')
    assert _s('-(2 * 3) * 4 + 5') == ('+', ('*', ('-', '0', ('*', '2', '3')), '4'), '5')


def test_plus_sign_isnt_negation():
    assert _s('+2') == '2'
    assert _s('+2 + (+3 * 4)') == ('+', '2', ('*', '3', '4'))
    assert _s('+ (+2 * 3)') == ('+', '0', ('*', '2', '3'))
