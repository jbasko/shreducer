import pytest

from shreducer_examples.grammars.filter_expressions import FilterExpressionsG

s = FilterExpressionsG.simple_parse


@pytest.mark.parametrize('op', ['eq', 'ne', 'gt', 'ge', 'lt', 'le'])
def test_parses_binary_comparison_operators(op):
    assert s('a {} b'.format(op)) == (op, 'a', 'b')


@pytest.mark.parametrize('op', ['and', 'or'])
def test_parses_binary_logical_operators(op):
    assert s('a eq b {} c ne d'.format(op)) == (op, ('eq', 'a', 'b'), ('ne', 'c', 'd'))


def test_logical_chain():
    assert s('a eq b and c eq d and e eq f and g eq h')


def test_parentheses():
    assert s('(a eq b and c eq d) or e eq f') == ('or', ('and', ('eq', 'a', 'b'), ('eq', 'c', 'd')), ('eq', 'e', 'f'))


def test_negation():
    assert s('not a eq b') == ('not', ('eq', 'a', 'b'))
    assert s('not a eq b or c ne d') == ('or', ('not', ('eq', 'a', 'b')), ('ne', 'c', 'd'))
    assert s('a eq b or not c eq d') == ('or', ('eq', 'a', 'b'), ('not', ('eq', 'c', 'd')))


@pytest.mark.parametrize('expr', [
    'not a',
    '(not a)'
    '(not a) gt b',
    'a gt not b',
    'a and (not b)',
])
def test_cannot_apply_negation_on_identifiers(expr):
    with pytest.raises(RuntimeError):
        s(expr)


def test_in_operator():
    assert s('a in b') == ('in', 'a', 'b')


def test_list_notation_with_parentheses():
    assert s('a in (b, c)') == ('in', 'a', ('list', ['b', 'c']))
    assert s('(a, b) in c') == ('in', ('list', ['a', 'b']), 'c')
    assert s('a in (b, c, d, e)') == ('in', 'a', ('list', ['b', 'c', 'd', 'e']))
    assert s('(a, b) in (c, d)') == ('in', ('list', ['a', 'b']), ('list', ['c', 'd']))

    assert s('not a in (b, c)') == ('not', ('in', 'a', ('list', ['b', 'c'])))
