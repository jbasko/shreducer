# Shreducers

Simple compilers in Python for fun and profit.

## Most Useful Thing in This Project

The most useful part of this project is the filter expressions parser.
You can use it to enable advanced filtering in your APIs with queries like this:

    https://your.api?filter=(status eq open and type eq store) or (status eq closed and type not in office, garage)

## Components

 * *Tokenizers* (no need to implement your own, we rely on `shlex` from Python Standard Library)
 * Grammars
 * *Parsers* (no need to implement your own, we use a *shift-reduce* parser, hence the name of the project)
 * Generators

**Tokenizer** splits input string into lexical units of the grammar (we call them tokens here).

**Grammar** describes the syntax rules of a language that we want to parse.

**Parser** parses sequence of tokens and generates a parse tree.
For example `('+', 2, ('-', 10, 3))` could be a parse tree.

**Generator** takes a parse tree and evaluates it. For example, an arithmetic generator could take 
a parse tree `('+', 2, ('-', 10, 3))` as an input and produce `9` as an output.

All these components together make a compiler.

    
## Implementing a New Grammar

See examples in `shreducers/examples/`:

 * `DictG` - simplest of all grammars, the most suitable to understand the basic idea, parser produces parsed dictionary
 * `ListG` - another simple grammar, but unlike dictionary grammar, parser for this one produces parse tree
 * `PlusMinusArithmeticsG` - simple arithmetic expression parser, parser produces parse tree
 * `BetterArithmeticsG` - arithmetic expression parser that respects operator precedence, parser produces parse tree
 * `FilterExpressionsG` - comparison operators and logical operators, parser produces parse tree
 * `BetterFiltersG` - comparatively rich filter expression language, unlike other grammars this one uses look-ahead,
    parser produces parse tree 

There is some magic (a meta class) going on in `t` class to allow
declaring a string constant without writing its value twice:

    class MyGrammar(Grammar):
        class t:
            IDENT = None
            PLUS_MINUS = '+-' 
            EXPR = ()

After the class `MyGrammar` is created, the value of `MyGrammar.t.IDENT` will be `"IDENT"`.
Similarly, `MyGrammar.t.PLUS_MINUS` will be `"PLUS_MINUS"`, and `MyGrammar.t.EXPR` will be `"EXPR"`.

Member of `class t` with value `None` is treated as the default token type.

Members of `class t` with value `()` are treated as names of tokens of higher order -- expressions.
