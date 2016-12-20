from shreducers import tokenizers
from shreducers.parser import ShiftReduceParser
from shreducers.tokenizers import EOF, EOF_VALUE


class GrammarMeta(type):
    def __new__(meta, name, bases, dct):
        token_type_lookup = {
            # Include EOF in all lookups
            EOF_VALUE: EOF
        }
        default_token_type = None

        for token_type, token_type_values in dct['t'].__dict__.iteritems():
            if token_type.startswith('_') or token_type.upper() != token_type:
                continue

            for v in token_type_values or ():
                token_type_lookup[v] = token_type

            # None denots default token type.
            # For tokens of higher abstraction (expressions) use empty tuple.
            if token_type_values is None:
                if default_token_type:
                    raise ValueError('More than one default token type declared: {} and {}'.format(
                        default_token_type, token_type
                    ))
                default_token_type = token_type

            # Replace token_type value with the string so it can be used as a constant
            dct['t'].__dict__[token_type] = token_type

        dct['_token_type_lookup'] = token_type_lookup
        dct['_default_token_type'] = default_token_type

        return super(GrammarMeta, meta).__new__(meta, name, bases, dct)


class Grammar(object):
    __metaclass__ = GrammarMeta

    class t:
        pass

    @classmethod
    def get_rules(cls):
        raise NotImplementedError()

    @classmethod
    def token_type(cls, token):
        return cls._token_type_lookup.get(token, cls._default_token_type)

    @classmethod
    def get_default_tokenizer(cls):
        return tokenizers.simple_tokenizer

    @classmethod
    def parse(cls, input_str, debug=False):
        return ShiftReduceParser(grammar=cls).parse(input_str, debug=debug)

    @classmethod
    def simple_parse(cls, input_str, debug=False):
        types, values = ShiftReduceParser(grammar=cls).parse(input_str, debug=debug)
        if len(types) == 1 and len(values) == 1:
            return values[0]
        elif len(types) == 2 and len(values) == 2 and types[1] is EOF and values[1] is EOF_VALUE:
            return values[0]
        else:
            raise RuntimeError('Parsing failed: {}, {}'.format(types, values))

