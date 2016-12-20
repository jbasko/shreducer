from shreducers.dummy_grammars.dict_grammar import DictG


def test_parses_dict_grammar():
    assert DictG.simple_parse('name: Bob') == {'name': 'Bob'}
    assert DictG.simple_parse('name : Bob , age:23') == {'name': 'Bob', 'age': '23'}
    assert DictG.simple_parse('name : Bob , age:23, "height": 183') == {'name': 'Bob', 'age': '23', '"height"': '183'}
    assert DictG.simple_parse('23: age') == {'23': 'age'}
