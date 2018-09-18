import copy

import pytest

from shreducer.parse_tree import ParseTreeMultiProcessor, ParseTreeProcessor, PtNode, PtNodeNotRecognised


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


def test_multi_processor_marks_is_root(parse_tree):
    pt = ParseTreeMultiProcessor(ParseTreeProcessor(), ParseTreeProcessor()).process(parse_tree)
    assert pt.x.is_root
    assert not pt.a.x.is_root
    assert not pt.b.x.is_root


def test_multi_processor_application_order():
    parse_tree = ('and', ('eq', 'a', 'b'), ('not', ('c')))
    calls = []

    class P1(ParseTreeProcessor):
        def process_unrecognised(self, node):
            calls.append(1)
            return node

    class P2(ParseTreeProcessor):
        def process_unrecognised(self, node):
            calls.append(2)
            return node

    class P3(ParseTreeProcessor):
        def process_unrecognised(self, node):
            calls.append(3)
            return node

    # Sequential processing with 2 slots
    pt1 = copy.deepcopy(parse_tree)
    ParseTreeMultiProcessor(P1()).slot(P2()).process(pt1)

    assert calls == [1, 1, 1, 2, 2, 2]

    calls[:] = []

    # Parallel processing with 1 slot
    pt2 = copy.deepcopy(parse_tree)
    ParseTreeMultiProcessor(P1(), P2()).process(pt2)

    assert calls == [1, 2, 1, 2, 1, 2]

    calls[:] = []

    # Parallel processing with 2 slots
    pt2 = copy.deepcopy(parse_tree)
    ParseTreeMultiProcessor(P1(), P2()).slot(P3()).process(pt2)

    assert calls == [1, 2, 1, 2, 1, 2, 3, 3, 3]


def test_strict_parse_tree_processor_raises_exception_on_unrecognised_nodes():
    class MyProcessor(ParseTreeProcessor):

        def process_or(self, node):
            return node

        def process_eq(self, node):
            return node

    ParseTreeProcessor(strict=False).process(('or', ('ne', 'a', 'b'), ('eq', 'c', 'd')))

    with pytest.raises(PtNodeNotRecognised) as excinfo:
        ParseTreeProcessor(strict=True).process(('or', ('ne', 'a', 'b'), ('eq', 'c', 'd')))

    exc = excinfo.value
    assert exc.node.to_tuple() == ('ne', 'a', 'b')


def test_strict_multi_processor_raises_exception_if_none_of_same_slot_processors_recognises_a_node():
    class LogicalOperatorProcessor(ParseTreeProcessor):
        @ParseTreeProcessor.delegate_of('process_and', 'process_or', 'process_not')
        def process_logical_ops(self, node):
            return node

    class ComparisonOperatorProcessor(ParseTreeProcessor):
        @ParseTreeProcessor.delegate_of('process_eq', 'process_ne')
        def process_comparison_ops(self, node):
            return node

    strict_proc = ParseTreeMultiProcessor().strict_slot(LogicalOperatorProcessor(), ComparisonOperatorProcessor())
    strict_proc.process(('or', ('ne', 'a', 'b'), ('eq', 'c', 'd')))

    with pytest.raises(PtNodeNotRecognised) as excinfo:
        strict_proc.process(('or', ('ne', 'a', 'b'), ('=', 'c', 'd')))

    exc = excinfo.value
    assert exc.node.to_tuple() == ('=', 'c', 'd')

    non_strict_proc = ParseTreeMultiProcessor().slot(LogicalOperatorProcessor(), ComparisonOperatorProcessor())
    non_strict_proc.process(('or', ('ne', 'a', 'b'), ('eq', 'c', 'd')))
    non_strict_proc.process(('or', ('ne', 'a', 'b'), ('=', 'c', 'd')))


def test_pre_order_processor_can_calculate_node_depth_in_one_pass(parse_tree):
    class DepthMarker(ParseTreeProcessor):
        pre_order = True

        def process_unrecognised(self, node):
            node.x.depth = node.x.depth or 0
            node.mark_operands(depth=node.x.depth + 1)
            return node

    proc = DepthMarker()

    pt = proc.process(('eq', 'a', 'b'))
    assert pt.x.depth == 0

    pt = proc.process(('and', ('eq', 'a', 'b'), ('ne', 'c', 'd')))
    assert pt.x.depth == 0
    assert pt.a.x.depth == 1
    assert pt.b.x.depth == 1

    pt = proc.process(parse_tree)
    assert pt.a.b.a.to_tuple() == ('eq', 'type', 'special')
    assert pt.a.b.a.x.depth == 3


def test_multi_processor_does_not_accept_post_and_pre_order_mix_in_one_slot():
    ParseTreeMultiProcessor(ParseTreeProcessor(pre_order=False), ParseTreeProcessor(pre_order=False))
    ParseTreeMultiProcessor(ParseTreeProcessor(pre_order=True), ParseTreeProcessor(pre_order=True))

    with pytest.raises(RuntimeError):
        ParseTreeMultiProcessor(ParseTreeProcessor(pre_order=True), ParseTreeProcessor(pre_order=False))

    with pytest.raises(RuntimeError):
        ParseTreeMultiProcessor(ParseTreeProcessor(pre_order=False), ParseTreeProcessor(pre_order=True))


def test_multi_processor_supports_pre_order(parse_tree):
    class DepthMarker(ParseTreeProcessor):
        pre_order = True

        def process_unrecognised(self, node):
            node.x.depth = node.x.depth or 0
            node.mark_operands(depth=node.x.depth + 1)
            return node

    proc = ParseTreeMultiProcessor(DepthMarker())

    pt = proc.process(('eq', 'a', 'b'))
    assert pt.x.depth == 0

    pt = proc.process(('and', ('eq', 'a', 'b'), ('ne', 'c', 'd')))
    assert pt.x.depth == 0
    assert pt.a.x.depth == 1
    assert pt.b.x.depth == 1

    pt = proc.process(parse_tree)
    assert pt.a.b.a.to_tuple() == ('eq', 'type', 'special')
    assert pt.a.b.a.x.depth == 3
