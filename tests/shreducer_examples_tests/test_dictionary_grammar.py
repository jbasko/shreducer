from shreducer_examples.grammars.dictionary import DictG

s = DictG.simple_parse


def test_parses_dict_grammar():
    assert s('name: Bob') == {'name': 'Bob'}
    assert s('name : Bob , age:23') == {'name': 'Bob', 'age': '23'}
    assert s('name : Bob , age:23, "height": 183') == {'name': 'Bob', 'age': '23', '"height"': '183'}
    assert s('23: age') == {'23': 'age'}
