# Shreducers

Simple parsers in Python for fun and profit.

## Usage

    >> from shreducers.examples.dict_grammar import DictG
    >> print DictG.simple_parse('name: Bob, age: 23')
    
    {'age': '23', 'name': 'Bob'}
    
## Implementing a New Grammar

See examples in `shreducers/examples/`:

 * `DictG` - simplest of all grammars, the most suitable to understand the basic idea
 * `PlusMinusArithmeticsG` -- simple arithmetic expression parser, produces syntax tree
 * `BetterArithmeticsG` -- arithmetic expression parser that respects operator precedence, produces syntax tree

There is some magic (a meta class) going on in `t` class to allow
declaring a string constant without writing its value twice:

    class MyGrammar(Grammar):
        class t:
            IDENT = None
            DIGITS = string.digits 
            EXPR = ()

After the class `MyGrammar` is created, the value of `MyGrammar.t.IDENT` will be `"IDENT"`.
Similarly, `MyGrammar.t.DIGITS` will be `"DIGITS"`, and `MyGrammar.t.EXPR` will be `"EXPR"`.

Member of `class t` with value `None` is treated as the default token type.

Members of `class t` with value `()` are treated as names of tokens of higher order -- expressions.
