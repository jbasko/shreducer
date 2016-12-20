from shreducers.examples.better_arithmetics import BetterArithmeticsG


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
