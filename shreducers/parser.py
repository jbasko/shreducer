import shlex


class ShiftReduceParser(object):
    def __init__(self, grammar=None, tokenizer=None):
        self.grammar = grammar
        self.rules = self.grammar.get_rules()
        self.tokenizer = tokenizer or shlex.shlex

    def parse(self, input_str):
        type_stack = []
        value_stack = []
        for v in self.tokenizer(input_str):
            t = self.grammar.token_type(v)
            type_stack.append(t)
            value_stack.append(v)
            self.apply_reducers(type_stack, value_stack)
        return type_stack, value_stack

    def apply_reducers(self, type_stack, value_stack):
        reducer_applied = True
        while reducer_applied:
            reducer_applied = False
            for rule, reducer in self.rules:
                if len(type_stack) < len(rule):
                    continue
                x = slice(-len(rule), None)
                if type_stack[x] != rule:
                    continue
                type_stack[x], value_stack[x] = reducer(type_stack[x], value_stack[x])
                reducer_applied = True
                break
