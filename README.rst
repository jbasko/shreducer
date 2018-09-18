=========
shreducer
=========

Simple compilers in Python for fun and profit.

-----------------------------------------
Example Grammars Included in This Project
-----------------------------------------

If you want to reuse the examples code, feel free to copy the code into your projects, but
do not introduce dependencies on examples as the examples may be changed or removed without notice.
Build your own grammar and related classes by extending classes provided in the `shreducer` package only.

* Python 3.6+ type hints string representation
* Filter expressions for web APIs. Allows parsing of expressions like this:
  ``https://your.api?filter=(status eq open and type eq store) or (status eq closed and type not in office, garage)``
* With a compiler of Elasticsearch queries included (not tested since 2016)
* A couple of primitive grammars for basic arithmetic expressions as examples

----------
Components
----------

* *Tokenizers* (no need to implement your own, we rely on ``shlex`` from Python Standard Library)
* Grammars
* *Parsers* (no need to implement your own, we use a *shift-reduce* parser, hence the name of the project)
* Generators

**Tokenizer** splits input string into lexical units of the grammar (we call them tokens here).

**Grammar** describes the syntax rules of a language that we want to parse.

**Parser** parses sequence of tokens and generates a parse tree.
For example ``('+', 2, ('-', 10, 3))`` could be a parse tree.

**Generator** takes a parse tree and evaluates it. For example, an arithmetic generator could take 
a parse tree ``('+', 2, ('-', 10, 3))`` as an input and produce ``9`` as an output.

All these components together make a compiler.

------------------------
Expressing a New Grammar
------------------------

See examples under ``shreducer_examples/``:

* ``DictG`` - simplest of all grammars, the most suitable to understand the basic idea, parser produces parsed dictionary
* ``ListG`` - another simple grammar, but unlike dictionary grammar, parser for this one produces parse tree
* ``PlusMinusArithmeticsG`` - simple arithmetic expression parser, parser produces parse tree
* ``BetterArithmeticsG`` - arithmetic expression parser that respects operator precedence, parser produces parse tree
* ``FilterExpressionsG`` - comparison operators and logical operators, parser produces parse tree
* ``BetterFiltersG`` - comparatively rich filter expression language, unlike other grammars this one uses look-ahead,
  parser produces parse tree
* ``TypeHintsG`` - parsing Python 3.6+ type hints string representation

There is some magic (a meta class) going on in ``t`` class to allow
declaring a string constant without writing its value twice:

.. code-block:: python

    class MyGrammar(Grammar):
        class t:
            IDENT = None
            PLUS_MINUS = '+-' 
            EXPR = ()


After the class ``MyGrammar`` is created, the value of ``MyGrammar.t.IDENT`` will be ``"IDENT"``.
Similarly, ``MyGrammar.t.PLUS_MINUS`` will be ``"PLUS_MINUS"``, and ``MyGrammar.t.EXPR`` will be ``"EXPR"``.

Member of ``class t`` with value ``None`` is treated as the default token type.

Members of ``class t`` with value ``()`` are treated as names of tokens of higher order -- expressions.

------------------------
Testing Your New Grammar
------------------------

If you implement just a grammar, you can try parsing input strings with ``Grammar.simple_parse`` (which is a class
method).

For example, to try ``TypeHintsG`` (grammar for parsing type hints string representation in Python 3.6+),
you can do:

.. code-block:: python

    print(TypeHintsG.simple_parse('typing.Union[typing.List[str], typing.Dict[str, int]]'))


This will produce the following parse tree:

.. code-block:: python

    {
        "name": "typing.Union",
        "args": [
            {
                "name": "typing.List",
                "args": [
                    {"name": "str", "args": None},
                ],
            },
            {
                "name": "typing.Dict",
                "args": [
                    {"name": "str", "args": None},
                    {"name": "int", "args": None},
                ],
            },
        ],
    }

