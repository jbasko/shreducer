import copy

import pytest

from shreducers.parse_tree import ParseTree


@pytest.fixture
def parse_tree():
    return (
        'and',
        ('or', ('in', 'off', 'tags'), ('eq', 'type', 'special')),
        ('gt', 'weight', '100'),
    )


def test_empty_parse_tree_is_initialised():
    pt = ParseTree()
    assert pt.op is None
    assert pt.a is None
    assert pt.b is None
    assert pt.x == {}
    assert pt.operands == (None,)
    assert pt.to_tuple() == (None, None)


def test_parse_tree_initialised_from_tuple():
    pt = ParseTree(('eq', 'type', 'special'))
    assert pt.op == 'eq'
    assert pt.a == 'type'
    assert pt.b == 'special'
    assert pt.x == {}
    assert pt.to_tuple() == ('eq', 'type', 'special')


def test_parse_tree_initialised_from_unnamed_args():
    pt = ParseTree('not', 'this')
    assert pt.op == 'not'
    assert pt.a == 'this'
    assert pt.b is None
    assert pt.x == {}
    assert pt.operands == ('this',)
    assert pt.to_tuple() == ('not', 'this')


def test_parse_tree_initialised_from_kwargs():
    pt = ParseTree(a='type', b='special', op='eq')
    assert pt.op == 'eq'
    assert pt.a == 'type'
    assert pt.b == 'special'
    assert pt.operands == ('type', 'special')
    assert pt.to_tuple() == ('eq', 'type', 'special')


def test_nested_parse_tree_initialised(parse_tree):
    parse_tree_copy = copy.deepcopy(parse_tree)

    pt = ParseTree(parse_tree)
    assert pt.op == 'and'
    assert pt.a[0] == 'or'
    assert pt.b[0] == 'gt'

    pt.a = ParseTree(pt.a)
    assert pt.a.op == 'or'

    pt.b = ParseTree(pt.b)
    assert pt.b.op == 'gt'

    assert pt.to_tuple() == parse_tree_copy


def test_parse_tree_extras(parse_tree):
    parse_tree_copy = copy.deepcopy(parse_tree)

    pt = ParseTree(parse_tree)
    assert pt.x == {}

    pt.x.i = 0
    assert pt.x.i == 0
    assert pt.x['i'] == 0
    assert 'i' in pt.x

    assert 'j' not in pt.x
    assert pt.x.j is None
    assert pt.x['j'] is None

    pt.x['j'] = 1
    assert pt.x.j == 1
    assert pt.x['j'] == 1

    assert 'k' not in pt.x
    assert pt.x['k'] is None
    assert pt.x.k is None

    pt.x.k = 2
    assert pt.x['k'] == 2
    assert pt.x.k == 2

    assert pt.to_tuple() == parse_tree_copy
