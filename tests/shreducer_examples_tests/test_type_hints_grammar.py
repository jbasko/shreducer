import pytest

from shreducer_examples.grammars.type_hints import TypeHintsG

s = TypeHintsG.simple_parse


@pytest.mark.parametrize('input_str,expected', [
    ['str', {'name': 'str', 'args': None}],
    ['typing.List[str]', {'name': 'typing.List', 'args': [{'name': 'str', 'args': None}]}]
])
def test_primitives(input_str, expected):
    assert expected == s(input_str)


def test_nested_composite():
    pt = s("typing.Union[None, typing.Dict[str, typing.Dict]]")
    assert pt['name'] == 'typing.Union'
    assert pt['args'][0] == {'name': 'None', 'args': None}
    assert pt['args'][1] == {'name': 'typing.Dict', 'args': [
        {'name': 'str', 'args': None},
        {'name': 'typing.Dict', 'args': None},
    ]}
