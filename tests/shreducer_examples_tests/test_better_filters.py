import pytest

from shreducer_examples.grammars.better_filters import BetterFiltersG

s = BetterFiltersG.simple_parse


def test_list_notation():
    assert s('a in b, c') == ('in', 'a', ('list', ['b', 'c']))
    assert s('(a in b, c)') == ('in', 'a', ('list', ['b', 'c']))
    assert s('a in b, c, d') == ('in', 'a', ('list', ['b', 'c', 'd']))

    assert s('a in (b, c)') == ('in', 'a', ('list', ['b', 'c']))
    assert s('a in (b, c, d)') == ('in', 'a', ('list', ['b', 'c', 'd']))
    assert s('a in b, (c, d)') == ('in', 'a', ('list', ['b', ('list', ['c', 'd'])]))
    assert s('a in (b, c), d') == ('in', 'a', ('list', [('list', ['b', 'c']), 'd']))

    assert s('a, b in c') == ('in', ('list', ['a', 'b']), 'c')
    assert s('(a, b in c)') == ('in', ('list', ['a', 'b']), 'c')
    assert s('a, b, c in d') == ('in', ('list', ['a', 'b', 'c']), 'd')

    assert s('(a, b) in c') == ('in', ('list', ['a', 'b']), 'c')
    assert s('(a, b, c) in d') == ('in', ('list', ['a', 'b', 'c']), 'd')
    assert s('a, (b, c) in d') == ('in', ('list', ['a', ('list', ['b', 'c'])]), 'd')
    assert s('(a, (b, c)) in d') == ('in', ('list', ['a', ('list', ['b', 'c'])]), 'd')
    assert s('(a, b), c in d') == ('in', ('list', [('list', ['a', 'b']), 'c']), 'd')
    assert s('((a, b), c) in d') == ('in', ('list', [('list', ['a', 'b']), 'c']), 'd')

    assert s('a, b in c, d') == ('in', ('list', ['a', 'b']), ('list', ['c', 'd']))
    assert s('(a, b) in (c, d)') == ('in', ('list', ['a', 'b']), ('list', ['c', 'd']))
    assert s('(a, b in c, d)') == ('in', ('list', ['a', 'b']), ('list', ['c', 'd']))


def test_not_in():
    assert s('a not in b') == s('not a in b') == s('not (a in b)')
    assert s('a not in b, c') == s('not a in b, c') == s('not (a in b, c)')


def test_logical_expressions_0():
    assert s('a eq b and c eq d') == ('and', ('eq', 'a', 'b'), ('eq', 'c', 'd'))


@pytest.mark.parametrize('input_str', [
    'a, b in c, d and e, f not in g, h',
    '(a, b) in c, d and e, f not in (g, h)',
    'a, b in (c, d) and (e, f) not in g, h',
    '(a, b in c, d) and e, f not in g, h',
    'a, b in c, d and (e, f not in g, h)',
    '(a, b in c, d) and (e, f not in g, h)',
    '(a, b in c, d and e, f not in g, h)',
])
def test_logical_expressions_1(input_str):
    assert s(input_str) == (
        'and',
        ('in', ('list', ['a', 'b']), ('list', ['c', 'd'])),
        ('not', ('in', ('list', ['e', 'f']), ('list', ['g', 'h'])))
    )


def test_dot_is_part_of_wordchars():
    s('some.field eq 44.50') == ('eq', 'some.field', '44.50')
