from shreducer.grammar import Grammar


def test_grammar_t_members_are_names_of_token_types():
    class MyGrammar(Grammar):
        class t:
            DIGIT = '0', '1', '2'
            SIGN = '+', '-'

    assert MyGrammar.t.DIGIT == 'DIGIT'
    assert MyGrammar.t.SIGN == 'SIGN'


def test_token_type_lookup_defaults_to_the_type():
    class MyGrammar(Grammar):
        class t:
            EXPR = ()  # empty tuple denotes a concept of higher abstraction
            DIGIT = '0', '1'
            UNKNOWN = None

    assert MyGrammar.token_type('0') == 'DIGIT'
    assert MyGrammar.token_type('1') == 'DIGIT'
    assert MyGrammar.token_type('2') == 'UNKNOWN'
