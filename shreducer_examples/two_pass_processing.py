"""
We have a filter expression which includes mentions of some fields that we need
to replace with values looked from a different service. We don't want to be making
the replacement calls as we encounter the foreign fields -- we want to do that only
after we have collected all the values.

Create collection in root node's x and hold on to that.

Note that there is no state in processors. All the state is stored on the nodes.
"""
from shreducer.parse_tree import ParseTreeInspector, ParseTreeMultiProcessor
from shreducer_examples import BetterFiltersG


def compile(input_str):

    # TODO Add tests for this one

    """
    This also demonstrates how to express basic processor using functions rather than classes.
    The function is used as process_unrecognised(node).
    It must include "_pre_" in name in order to be registered as pre_order processor.
    """

    def contacts_pre_processor(node):
        # Initialise state in the root
        if node.x.is_root:
            node.x.foreign_lookups = {}
        node.mark_operands(foreign_lookups=node.x.foreign_lookups)
        if node.is_leaf and 'contacts.' in node.a:
            node.x.foreign_lookups[node.a] = node.b
        return node

    def contacts_post_processor(node):
        if node.x.is_root:
            # Do the lookups
            for k, v in node.x.foreign_lookups.items():
                node.x.foreign_lookups[k] = '<looked-up-value-of-{}>'.format(v)

        # Dummy replacement
        if node.is_leaf and node.a in node.x.foreign_lookups:
            node.b = node.x.foreign_lookups[node.a]

        return node

    parse_tree = BetterFiltersG.simple_parse(input_str)
    return (
        ParseTreeMultiProcessor()
        .slot(contacts_pre_processor)
        .slot(ParseTreeInspector())
        .slot(contacts_post_processor)
        .slot(ParseTreeInspector())
    ).process(parse_tree)


compile('(type eq main and contacts.name eq "JB") or (contacts.name ne "JB" and type eq other)')
