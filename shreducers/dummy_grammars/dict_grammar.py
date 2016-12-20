from shreducers.grammar import Grammar


class DictG(Grammar):
    class t:
        IDENT = None
        COLON = ':',
        COMMA = ',',
        DICT = None

    @classmethod
    def get_rules(cls):
        return [
            ([cls.t.IDENT, cls.t.COLON, cls.t.IDENT], cls.create_dictionary),
            ([cls.t.DICT, cls.t.COMMA, cls.t.DICT], cls.update_dictionary),
        ]

    @classmethod
    def create_dictionary(cls, types, (key, colon, value)):
        return [cls.t.DICT], [{key: value}]

    @classmethod
    def update_dictionary(cls, types, (dict1, comma, dict2)):
        return [cls.t.DICT], [dict(dict1, **dict2)]
