class ShiftReduceParser(object):
    def __init__(self, grammar=None, tokenizer=None):
        self.grammar = grammar
        # get_rules can either return a list or be a generator
        self.rules = list(self.grammar.get_rules())
        self.tokenizer = tokenizer or self.grammar.get_default_tokenizer()

    def _print_state(self, type_stack, value_stack):
        print('\t', type_stack)
        print('\t', value_stack)

    @classmethod
    def tokenize_with_lookahead(cls, tokenizer, input_str):
        """
        Yields (token, lookahead) one by one.
        Lookahead is None for the last token.
        """
        prev_token = None
        current_token = None
        for current_token in tokenizer(input_str):
            if prev_token is not None:
                yield prev_token, current_token
            prev_token = current_token

        if current_token is not None:
            yield current_token, None

    def parse(self, input_str, debug=False):
        type_stack = []
        value_stack = []

        for v, lookahead in self.tokenize_with_lookahead(self.tokenizer, input_str):
            t = self.grammar.token_type(v)
            lookahead_type = None if lookahead is None else self.grammar.token_type(lookahead)
            type_stack.append(t)
            value_stack.append(v)
            if debug:
                print('Shifted')
                self._print_state(type_stack, value_stack)
            self.apply_reducers(type_stack, value_stack, lookahead_type=lookahead_type, debug=debug)

        if debug:
            print('Completed')
            self._print_state(type_stack, value_stack)

        return type_stack, value_stack

    def apply_reducers(self, type_stack, value_stack, lookahead_type=None, debug=False):
        reducer_applied = True
        while reducer_applied:
            reducer_applied = False
            for rule in self.rules:
                if len(type_stack) < len(rule[0]):
                    continue

                if len(rule) == 2:
                    rule_prefix, rule_reducer = rule
                    rule_lookahead = None
                else:
                    rule_prefix, rule_lookahead, rule_reducer = rule

                x = slice(-len(rule_prefix), None)
                if type_stack[x] != rule_prefix or (rule_lookahead is not None and rule_lookahead != lookahead_type):
                    continue
                type_stack[x], value_stack[x] = rule_reducer(type_stack[x], value_stack[x])
                reducer_applied = True
                if debug:
                    print('Reduced')
                    self._print_state(type_stack, value_stack)
                break
