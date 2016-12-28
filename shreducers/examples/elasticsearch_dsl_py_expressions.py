"""
An example how to go about implementing expressions compiler to use with elasticsearch-dsl-py library.
"""

import collections
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as es_dsl_Search, Q, F

from shreducers.examples.grammars.better_filters import BetterFiltersG


Node = collections.namedtuple('Node', field_names=('op', 'a', 'b', 'x'))
Node.__new__.__defaults__ = (None, None, None, None)


class FilterPreprocessor(object):
    def process_node(self, node):
        if not isinstance(node, tuple):
            return node
        if not isinstance(node, Node):
            node = Node(*node)
        processor_name = 'process_{}'.format(node.op)
        if hasattr(self, processor_name):
            node = getattr(self, processor_name)(node)
        else:
            if node.a:
                node = node._replace(a=self.process_node(node.a))
            if node.b:
                node = node._replace(b=self.process_node(node.b))
        return node

    def process_list(self, node):
        return node.a


class EsDslFilterPreprocessor(FilterPreprocessor):
    def process_eq(self, node):
        return node._replace(a='{}.raw'.format(node.a))


class FilterGenerator(object):
    def generate(self, node):
        if isinstance(node, Node):
            return getattr(self, 'generate_{}'.format(node.op))(node)
        else:
            return node


class EsDslFilterGenerator(FilterGenerator):
    def generate_eq(self, node):
        return F('term', **{node.a: node.b})

    def generate_ne(self, node):
        return ~self.generate_eq(node)

    def generate_and(self, node):
        return self.generate(node.a) & self.generate(node.b)

    def generate_or(self, node):
        return self.generate(node.a) | self.generate(node.b)

    def generate_not(self, node):
        return ~self.generate(node.a)

    def generate_in(self, node):
        return F('terms', **{node.a: node.b})


class EsDslFilterExpressionsCompiler(object):
    def __init__(self):
        self._grammar = BetterFiltersG
        self._generator = EsDslFilterGenerator()
        self._preprocessor = EsDslFilterPreprocessor()

    def compile(self, input_str):
        parse_tree = self._grammar.simple_parse(input_str)
        parse_tree = self._preprocessor.process_node(parse_tree)
        return self._generator.generate(parse_tree)


client = Elasticsearch()


class Search(es_dsl_Search):
    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self._filter_expr_compiler = EsDslFilterExpressionsCompiler()

    def filter_expr(self, input_str):
        return self.filter(self._filter_expr_compiler.compile(input_str))


s = Search(using=client, index='things').filter_expr('status in open, temporarily_closed or status ne closed')
# print s.to_dict()
for hit in s.execute():
    print hit.meta.score, hit.name, hit.type
