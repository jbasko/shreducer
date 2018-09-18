from shreducer import Grammar


class ListG(Grammar):
    class t:
        ID = None
        COMMA = ','
        PARENS_OPEN = '('
        PARENS_CLOSE = ')'
        LIST = ()

        # An ID or LIST that is completed and cannot be modified anymore
        # DONE must have all the rules that ID has.
        DONE = ()

    @classmethod
    def get_rules(cls):
        return [
            ([cls.t.ID, cls.t.COMMA], cls.begin_list),
            ([cls.t.DONE, cls.t.COMMA], cls.begin_list),
            ([cls.t.LIST, cls.t.COMMA, cls.t.ID], cls.append_to_list),
            ([cls.t.LIST, cls.t.COMMA, cls.t.DONE], cls.append_to_list),

            ([cls.t.PARENS_OPEN, cls.t.LIST, cls.t.PARENS_CLOSE], cls.remove_parens),
            ([cls.t.PARENS_OPEN, cls.t.ID, cls.t.PARENS_CLOSE], cls.single_item_list),
        ]

    @classmethod
    def begin_list(cls, types, xxx_todo_changeme):
        (a, comma) = xxx_todo_changeme
        return [cls.t.LIST, cls.t.COMMA], [('list', [a]), comma]

    @classmethod
    def append_to_list(cls, types, xxx_todo_changeme1):
        (head, comma, a) = xxx_todo_changeme1
        head[1].append(a)
        return [cls.t.LIST], [head]

    @classmethod
    def remove_parens(cls, types, xxx_todo_changeme2):
        (p1, a, p2) = xxx_todo_changeme2
        return [cls.t.DONE], [a]

    @classmethod
    def single_item_list(cls, types, xxx_todo_changeme3):
        (p1, a, p2) = xxx_todo_changeme3
        return [cls.t.DONE], [('list', [a])]
