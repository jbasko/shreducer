import shlex


class _Eof(object):
    def __repr__(self):
        return '<EOF_VALUE>'


EOF_VALUE = _Eof()
EOF = 'EOF'


def create_shlex_tokenizer(with_eof=False, **settings):
    """
    See what attributes can be set on shlex:
    https://docs.python.org/2/library/shlex.html#shlex-objects

    For example, for simple arithmetic parsers you probably want to add dot "." to wordchars:
        custom_tokenizer(..., wordchars=string.digits + '.')
    """
    def custom_tokenizer(input_str):
        tokenizer = shlex.shlex(input_str)
        for k, v in settings.iteritems():
            setattr(tokenizer, k, v)
        for t in tokenizer:
            yield t
        if with_eof:
            yield EOF_VALUE
    return custom_tokenizer

