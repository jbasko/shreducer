"""
Parse string-representation of type hints.

 * typing.List[str]
 * typing.List
 * typing.Dict[str, str]
 * typing.Union[None, typing.Dict[str, typing.Dict]]

 Need a BOF

"""
import string

from shreducers.grammar import Grammar
from shreducers.tokenizers import create_shlex_tokenizer


class TypeHintsG(Grammar):
    class t:
        IDENT = None
        PARENS_OPEN = '['
        PARENS_CLOSE = ']'
        COMMA = ','
        ARGS_LIST = ()
        TYPE_DEF = ()

    @classmethod
    def get_default_tokenizer(cls):
        return create_shlex_tokenizer(
            wordchars=string.ascii_uppercase + string.ascii_lowercase + string.digits + '_.',
        )

    @classmethod
    def get_rules(cls):
        return [
            ([cls.t.IDENT], cls.create_primitive_type_def),
            ([cls.t.TYPE_DEF, cls.t.COMMA, cls.t.TYPE_DEF], cls.create_args_list),
            ([cls.t.ARGS_LIST, cls.t.COMMA, cls.t.TYPE_DEF], cls.append_to_args_list),
            ([cls.t.TYPE_DEF, cls.t.PARENS_OPEN, cls.t.ARGS_LIST, cls.t.PARENS_CLOSE], cls.create_composite_type_def),
            ([cls.t.TYPE_DEF, cls.t.PARENS_OPEN, cls.t.TYPE_DEF, cls.t.PARENS_CLOSE], cls.create_composite_type_def),
        ]

    @classmethod
    def create_primitive_type_def(cls, types, values):
        type_name, = values
        return [cls.t.TYPE_DEF], [{'name': type_name, 'args': []}]

    @classmethod
    def create_args_list(cls, types, values):
        first, _, second = values
        return [cls.t.ARGS_LIST], [{'args': [first, second]}]

    @classmethod
    def append_to_args_list(cls, types, values):
        args_list, _, item = values
        args_list['args'].append(item)
        return [cls.t.ARGS_LIST], [args_list]

    @classmethod
    def create_composite_type_def(cls, types, values):
        name_comp, _, args_list, _ = values
        if types[2] is cls.t.ARGS_LIST:
            # Multiple arguments
            return [cls.t.TYPE_DEF], [{'name': name_comp['name'], 'args': args_list['args']}]
        elif types[2] is cls.t.TYPE_DEF:
            # Single argument
            return [cls.t.TYPE_DEF], [{'name': name_comp['name'], 'args': [args_list]}]

# TypeHintsG.parse("str", debug=True)
# print(TypeHintsG.simple_parse("str"))

# TypeHintsG.parse("typing.List[str]", debug=True)
# print(TypeHintsG.simple_parse("typing.List[str]"))

TypeHintsG.parse("typing.Union[None, typing.Dict[str, typing.Dict]]", debug=True)
print(TypeHintsG.simple_parse("typing.Union[None, typing.Dict[str, typing.Dict]]"))
