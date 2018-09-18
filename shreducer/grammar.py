from shreducer import tokenizers
from shreducer.parser import ShiftReduceParser
from shreducer.tokenizers import BOF, BOF_VALUE, EOF, EOF_VALUE


class GrammarMeta(type):
    def __new__(meta, name, bases, dct):
        token_type_lookup = {
            # Include BOF and EOF in all lookups
            BOF_VALUE: BOF,
            EOF_VALUE: EOF,
        }
        default_token_type = None

        if 't' not in dct:
            raise RuntimeError('Grammar class {} declaration is missing inner class "t"'.format(name))

        for token_type, token_type_values in dct['t'].__dict__.items():
            if token_type.startswith('_') or token_type.upper() != token_type:
                continue

            for v in token_type_values or ():
                if v in token_type_lookup:
                    raise RuntimeError('Value {!r} mentioned in more than one token type listing'.format(v))
                token_type_lookup[v] = token_type

            # None denotes default token type.
            # For tokens of higher abstraction (expressions) use empty tuple.
            if token_type_values is None:
                if default_token_type:
                    raise RuntimeError('More than one default token type declared: {} and {}'.format(
                        default_token_type, token_type
                    ))
                default_token_type = token_type

            # Replace token_type value with the string so it can be used as a constant
            setattr(dct['t'], token_type, token_type)

        dct['_token_type_lookup'] = token_type_lookup
        dct['_default_token_type'] = default_token_type

        return super(GrammarMeta, meta).__new__(meta, name, bases, dct)


class Grammar(object, metaclass=GrammarMeta):
    class t:
        pass

    @classmethod
    def get_rules(cls):
        """
        This can be either a generator or just return a list of rules.
        For non-trivial grammars it's more convenient to use a generator
        as some rules are repetitive.
        """
        raise NotImplementedError()

    @classmethod
    def token_type(cls, token):
        return cls._token_type_lookup.get(token, cls._default_token_type)

    @classmethod
    def get_default_tokenizer(cls):
        return tokenizers.create_shlex_tokenizer()

    @classmethod
    def parse(cls, input_str, debug=False):
        return ShiftReduceParser(grammar=cls).parse(input_str, debug=debug)

    @classmethod
    def simple_parse(cls, input_str, debug=False):
        types, values = ShiftReduceParser(grammar=cls).parse(input_str, debug=debug)
        if len(types) == 1 and len(values) == 1:
            return values[0]
        elif len(types) == 2 and len(values) == 2 and (types[0], values[0]) == (BOF, BOF_VALUE):
            return values[1]
        elif len(types) == 2 and len(values) == 2 and (types[1], values[1]) == (EOF, EOF_VALUE):
            return values[0]
        elif (
            len(types) == 3 and len(values) == 3 and
            (types[0], values[0], types[2], values[2]) == (BOF, BOF_VALUE, EOF, EOF_VALUE)
        ):
            return values[1]
        else:
            raise RuntimeError('Parsing failed: {}, {}'.format(types, values))
