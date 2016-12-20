class ShiftReduceParser(object):
    def __init__(self, grammar=None, tokenizer=None):
        self.grammar = grammar
        self.rules = self.grammar.get_rules()
        self.tokenizer = tokenizer or self.grammar.get_default_tokenizer()

    def parse(self, input_str, debug=False):
        type_stack = []
        value_stack = []
        for i, v in enumerate(self.tokenizer(input_str)):
            t = self.grammar.token_type(v)
            type_stack.append(t)
            value_stack.append(v)
            self.apply_reducers(type_stack, value_stack)
            if debug:
                print i
                print '\t', type_stack
                print '\t', value_stack
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
