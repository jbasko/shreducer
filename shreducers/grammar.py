from shreducers.parser import ShiftReduceParser


class GrammarMeta(type):
    def __new__(meta, name, bases, dct):
        token_type_lookup = {}
        default_token_type = None

        for token_type, token_type_values in dct['t'].__dict__.iteritems():
            if token_type.startswith('_') or token_type.upper() != token_type:
                continue

            for v in token_type_values or ():
                token_type_lookup[v] = token_type

            if not token_type_values and default_token_type is None:
                # The first token type with no values is the default token type
                default_token_type = token_type

            # Replace token_type value with the string so it can be used as a constant
            dct['t'].__dict__[token_type] = token_type

        dct['_token_type_lookup'] = token_type_lookup
        dct['_default_token_type'] = default_token_type

        # Must also fix rules because they refer to the wrong things!


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
    def parse(cls, input_str):
        return ShiftReduceParser(grammar=cls).parse(input_str)

    @classmethod
    def simple_parse(cls, input_str):
        types, values = ShiftReduceParser(grammar=cls).parse(input_str)
        if len(types) != 1 or len(values) != 1:
            raise RuntimeError('Parsing failed: {}, {}'.format(types, values))
        return values[0]
