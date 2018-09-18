from shreducer_examples.grammars.list_grammar import ListG

s = ListG.simple_parse


def test_single_item_list():
    assert s('(1)') == ('list', ['1'])


def test_multi_item_list():
    assert s('1, 2, 3') == ('list', ['1', '2', '3'])
    assert s('(1, 2, 3)') == ('list', ['1', '2', '3'])


def test_list_of_lists():
    assert s('1, (2, 3, 4), 5') == ('list', ['1', ('list', ['2', '3', '4']), '5'])
    assert s('(1, 2), 3, 4') == ('list', [('list', ['1', '2']), '3', '4'])
    assert s('(1), (2), (3, 4), (5, (6, 7))')
