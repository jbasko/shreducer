import copy

import pytest

from shreducers.parse_tree import PtNode, ParseTreeProcessor, ParseTreeMultiProcessor


@pytest.fixture
def parse_tree():
    return (
        'and',
        ('or', ('in', 'off', 'tags'), ('not', ('eq', 'type', 'special'))),
        ('gt', 'weight', '100'),
    )


def test_empty_pt_node_is_initialised():
    pt = PtNode()
    assert pt.op is None
    assert pt.a is None
    assert pt.b is None
    assert pt.x == {}
    assert pt.operands == (None,)
    assert pt.to_tuple() == (None, None)


def test_pt_node_initialised_from_tuple():
    pt = PtNode(('eq', 'type', 'special'))
    assert pt.op == 'eq'
    assert pt.a == 'type'
    assert pt.b == 'special'
    assert pt.x == {}
    assert pt.to_tuple() == ('eq', 'type', 'special')


def test_pt_node_initialised_from_unnamed_args():
    pt = PtNode('not', 'this')
    assert pt.op == 'not'
    assert pt.a == 'this'
    assert pt.b is None
    assert pt.x == {}
    assert pt.operands == ('this',)
    assert pt.to_tuple() == ('not', 'this')


def test_parse_tree_initialised_from_kwargs():
    pt = PtNode(a='type', b='special', op='eq')
    assert pt.op == 'eq'
    assert pt.a == 'type'
    assert pt.b == 'special'
    assert pt.operands == ('type', 'special')
    assert pt.to_tuple() == ('eq', 'type', 'special')


def test_nested_parse_tree_initialised(parse_tree):
    parse_tree_copy = copy.deepcopy(parse_tree)

    pt = PtNode(parse_tree)
    assert pt.op == 'and'
    assert pt.a.op == 'or'
    assert pt.b.op == 'gt'

    assert pt.a.op == 'or'

    assert pt.b.op == 'gt'

    assert pt.to_tuple() == parse_tree_copy


def test_pt_node_extras(parse_tree):
    parse_tree_copy = copy.deepcopy(parse_tree)

    pt = PtNode(parse_tree)
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


def test_parse_tree_processor_visits_every_node(parse_tree):
    class MyProcessor(ParseTreeProcessor):
        def process_primitive(self, primitive):
            return '{}!'.format(primitive)

        def process_gt(self, parse_tree):
            parse_tree.op = 'GREATER_THAN'
            return parse_tree

        def process_unrecognised(self, parse_tree):
            parse_tree.op = '{}!'.format(parse_tree.op)
            return parse_tree

    pt = MyProcessor().process(parse_tree)
    assert pt.op == 'and!'
    assert pt.a.op == 'or!'
    assert pt.b.op == 'GREATER_THAN'
    assert pt.b.a == 'weight!'
    assert pt.b.b == '100!'


def test_pt_node_marks_operands(parse_tree):
    class MyProcessor(ParseTreeProcessor):
        def process_unrecognised(self, node):
            node.mark_operands(visited_by_my_processor=True)
            return node

    pt = MyProcessor().process(parse_tree)
    assert pt.x.visited_by_my_processor is None
    assert pt.a.x.visited_by_my_processor is True
    assert pt.a.a.x.visited_by_my_processor is True
    assert pt.b.x.visited_by_my_processor is True


def test_parse_tree_multiprocessor_calls_all_processors(parse_tree):
    class PrimitivesProcessor(ParseTreeProcessor):
        def process_primitive(self, primitive):
            return '{}!'.format(primitive)

    class OperatorsProcessor(ParseTreeProcessor):
        def process_unrecognised(self, parse_tree):
            parse_tree.op = '<{}>'.format(parse_tree.op)
            return parse_tree

    class PostProcessor(ParseTreeProcessor):
        def process_primitive(self, primitive):
            return '{}?'.format(primitive)

    proc = ParseTreeMultiProcessor(PrimitivesProcessor(), OperatorsProcessor(), PostProcessor())
    pt = proc.process(parse_tree)

    t = pt.to_tuple()
    assert t[0] == '<and>'
    assert t[1] == ('<or>', ('<in>', 'off!?', 'tags!?'), ('<not>', ('<eq>', 'type!?', 'special!?')))
    assert t[2] == ('<gt>', 'weight!?', '100!?')


def test_delegate_of_decorator_delegates_method(parse_tree):
    class CustomProcessor(ParseTreeProcessor):
        @ParseTreeProcessor.delegate_of(
            'process_in',
            'process_gt',
            'process_eq',
        )
        def process_custom(self, parse_tree):
            parse_tree.op = '<{}>'.format(parse_tree.op)
            return parse_tree

    pt = CustomProcessor().process(parse_tree)
    t = pt.to_tuple()
    assert t[0] == 'and'
    assert t[1] == ('or', ('<in>', 'off', 'tags'), ('not', ('<eq>', 'type', 'special')))
    assert t[2] == ('<gt>', 'weight', '100')


def test_multi_processor_with_no_processors_does_nothing(parse_tree):
    parse_tree_copy = copy.deepcopy(parse_tree)
    pt = ParseTreeMultiProcessor().process(parse_tree)
    assert pt.to_tuple() == parse_tree_copy


def test_cannot_extend_multi_processor_cls():
    class MyMultiProcessor(ParseTreeMultiProcessor):
        pass

    with pytest.raises(RuntimeError):
        MyMultiProcessor(ParseTreeProcessor())
