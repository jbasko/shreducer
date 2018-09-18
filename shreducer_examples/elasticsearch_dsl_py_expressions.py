"""
An example how to go about implementing expressions compiler to use with elasticsearch-dsl-py library.
"""

from elasticsearch import Elasticsearch
from elasticsearch_dsl import F
from elasticsearch_dsl import Search as es_dsl_Search
from shreducer.parse_tree import ParseTreeMultiProcessor, ParseTreeProcessor
from shreducer_examples import BetterFiltersG


class EsDslFilterPreprocessor(ParseTreeProcessor):
    def process_list(self, node):
        return node.a


class EsDslFilterGenerator(ParseTreeProcessor):
    def process_eq(self, node):
        return F('term', **{'{}.raw'.format(node.a): node.b})

    def process_ne(self, node):
        return ~self.process_eq(node)

    def process_and(self, node):
        return node.a & node.b

    def process_or(self, node):
        return node.a | node.b

    def process_not(self, node):
        return ~node.a

    def process_in(self, node):
        return F('terms', **{node.a: node.b})


class EsDslFilterExpressionsCompiler(object):
    def __init__(self):
        self._grammar = BetterFiltersG
        self._proc = (
            ParseTreeMultiProcessor()
            .slot(EsDslFilterPreprocessor())
            .strict_slot(EsDslFilterGenerator())
        )

    def compile(self, input_str):
        parse_tree = self._grammar.simple_parse(input_str)
        return self._proc.process(parse_tree)


client = Elasticsearch()


class Search(es_dsl_Search):
    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self._filter_expr_compiler = EsDslFilterExpressionsCompiler()

    def filter_expr(self, input_str):
        return self.filter(self._filter_expr_compiler.compile(input_str))


s = Search(
    using=client, index='things',
).filter_expr('status in open, temporarily_closed or status ne closed and type eq local')
print(s.to_dict())
for hit in s.execute():
    print(hit.meta.score, hit.name, hit.type)
