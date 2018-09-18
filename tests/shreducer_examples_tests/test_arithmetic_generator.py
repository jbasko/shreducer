from shreducer_examples.generators.arithmetic import ArithmeticGenerator
from shreducer_examples.grammars.plus_minus_arithmetics import PlusMinusArithmeticsG


def e(input_str):
    return ArithmeticGenerator().run(PlusMinusArithmeticsG.simple_parse(input_str))


g = ArithmeticGenerator()


def test_generates_numbers_from_non_tuples():
    assert g.run('5') == 5
    assert g.run('5.5') == 5.5
    assert g.run('55.55') == 55.55
    assert g.run('55.00') == 55.0


def test_evalutes_plus_minus_arithmetics():
    assert e('5') == 5
    assert e('2 + 3') == 5
    assert e('2 - 3') == -1
    assert e('2 - 3 + 5') == 4
    assert e('23 - 2') == 21
    assert e('23.22 - 2') == 21.22
