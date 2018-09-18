from shreducer import tokenizers
from shreducer.parser import ShiftReduceParser
from shreducer.tokenizers import BOF_VALUE, EOF_VALUE


def test_basic_tokenizer_yields_token_and_lookahead():
    tokenizer = tokenizers.create_shlex_tokenizer()

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, ''))
    assert len(tokens) == 0

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, 'a b c'))
    assert len(tokens) == 3
    assert tokens[0] == ('a', 'b')
    assert tokens[1] == ('b', 'c')
    assert tokens[2] == ('c', None)


def test_tokenizer_with_eof_yields_token_and_lookahead():
    tokenizer = tokenizers.create_shlex_tokenizer(with_eof=True)

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, ''))
    assert len(tokens) == 1
    assert tokens[0] == (EOF_VALUE, None)

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, 'a b c'))
    assert len(tokens) == 4
    assert tokens[0] == ('a', 'b')
    assert tokens[1] == ('b', 'c')
    assert tokens[2] == ('c', EOF_VALUE)
    assert tokens[3] == (EOF_VALUE, None)


def test_tokenizer_with_bof_yields_token_and_lookahead():
    tokenizer = tokenizers.create_shlex_tokenizer(with_bof=True)

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, ''))
    assert len(tokens) == 1
    assert tokens[0] == (BOF_VALUE, None)

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, 'a b c'))
    assert len(tokens) == 4
    assert tokens[0] == (BOF_VALUE, 'a')
    assert tokens[1] == ('a', 'b')
    assert tokens[2] == ('b', 'c')
    assert tokens[3] == ('c', None)


def test_tokenizer_with_bof_and_eof_yields_token_and_lookahead():
    tokenizer = tokenizers.create_shlex_tokenizer(with_bof=True, with_eof=True)

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, ''))
    assert len(tokens) == 2
    assert tokens[0] == (BOF_VALUE, EOF_VALUE)
    assert tokens[1] == (EOF_VALUE, None)

    tokens = list(ShiftReduceParser.tokenize_with_lookahead(tokenizer, 'a b c'))
    assert len(tokens) == 5
    assert tokens[0] == (BOF_VALUE, 'a')
    assert tokens[1] == ('a', 'b')
    assert tokens[2] == ('b', 'c')
    assert tokens[3] == ('c', EOF_VALUE)
    assert tokens[4] == (EOF_VALUE, None)
