import shlex


class _Eof(object):
    def __repr__(self):
        return '<EOF_VALUE>'


EOF_VALUE = _Eof()
EOF = 'EOF'


def simple_tokenizer(input_str):
    for t in shlex.shlex(input_str):
        yield t


def tokenizer_with_eof(input_str):
    for t in simple_tokenizer(input_str):
        yield t
    yield EOF_VALUE
