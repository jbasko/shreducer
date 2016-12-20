# Shreducers

Simple parsers in Python for fun and profit.

## Usage

    >> from shreducers.examples.dict_grammar import DictG
    >> print DictG.simple_parse('name: Bob, age: 23')
    
    {'age': '23', 'name': 'Bob'}
    
## Implementing a New Grammar

See examples in `shreducers/examples/`.
