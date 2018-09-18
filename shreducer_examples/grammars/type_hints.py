import string

from shreducer.grammar import Grammar
from shreducer.tokenizers import create_shlex_tokenizer


class TypeHintsG(Grammar):
    """
    Grammar for string representation of type hints in Python 3.6+

    Just a few shreducer_examples of valid input strings:

     - "str"
     - "typing.List"
     - "typing.List[str]"
     - "typing.Dict[str, str]"
     - "typing.Union[None, typing.Dict[str, str]]"

    """

    class t:
        IDENT = None
        BRACKETS_OPEN = '['
        BRACKETS_CLOSE = ']'
        COMMA = ','
        ARGS_LIST_ITEMS = ()
        TYPE_DEF = ()

    @classmethod
    def get_default_tokenizer(cls):
        return create_shlex_tokenizer(
            wordchars=string.ascii_uppercase + string.ascii_lowercase + string.digits + '_.',
        )

    @classmethod
    def get_rules(cls):
        """
        Argument list aggregation can only start once we see the closing bracket.

        "IDENT" -> "TYPE_DEF"
        "TYPE_DEF ]" -> "ARGS_LIST_ITEMS ]"
        "TYPE_DEF , ARGS_LIST_ITEMS ]" -> "ARGS_LIST_ITEMS ]"
        "TYPE_DEF [ ARGS_LIST_ITEMS ]" -> "TYPE_DEF"

        """
        return [
            (
                [cls.t.IDENT],
                cls.create_primitive_type_def,
            ),
            (
                [cls.t.TYPE_DEF, cls.t.BRACKETS_CLOSE],
                cls.create_args_list_items
            ),
            (
                [cls.t.TYPE_DEF, cls.t.COMMA, cls.t.ARGS_LIST_ITEMS, cls.t.BRACKETS_CLOSE],
                cls.prepend_to_args_list_items
            ),
            (
                [cls.t.TYPE_DEF, cls.t.BRACKETS_OPEN, cls.t.ARGS_LIST_ITEMS, cls.t.BRACKETS_CLOSE],
                cls.create_composite_type_def
            ),
        ]

    @classmethod
    def create_primitive_type_def(cls, types, values):
        type_name, = values
        return [cls.t.TYPE_DEF], [{'name': type_name, 'args': None}]

    @classmethod
    def create_args_list_items(cls, types, values):
        type_def, brackets_close = values
        return [cls.t.ARGS_LIST_ITEMS, cls.t.BRACKETS_CLOSE], [[type_def], brackets_close]

    @classmethod
    def prepend_to_args_list_items(cls, types, values):
        type_def, _, args_list_items, brackets_close = values
        args_list_items.insert(0, type_def)
        return [cls.t.ARGS_LIST_ITEMS, cls.t.BRACKETS_CLOSE], [args_list_items, brackets_close]

    @classmethod
    def create_composite_type_def(cls, types, values):
        type_def, brackets_open, args_list_items, brackets_close = values
        return [cls.t.TYPE_DEF], [{'name': type_def['name'], 'args': args_list_items}]
